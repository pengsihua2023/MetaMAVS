"""Tests for Phase 2 real command execution machinery."""

from __future__ import annotations

import textwrap
from pathlib import Path

import yaml

from metamavs.config import load_config
from metamavs.utils.command_runner import CommandRunner
from metamavs.utils.execution import check_tools, make_runner, maybe_execute_step
from metamavs.workflows.local_workflow import run_local_workflow


def _state(dry_run: bool, retries: int = 0):
    return {
        "config": {"execution": {"threads": 4, "retries": retries}},
        "dry_run": dry_run,
    }


# ---- tool availability ------------------------------------------------------

def test_tool_available_true_for_real_binary():
    # Python always has a shell with `sh`; use a near-universal tool.
    assert CommandRunner.tool_available("sh") is True


def test_tool_available_false_for_fake():
    assert CommandRunner.tool_available("definitely_not_a_real_tool_xyz") is False


def test_check_tools_map():
    result = check_tools(["sh", "definitely_not_a_real_tool_xyz"])
    assert result["sh"] is True
    assert result["definitely_not_a_real_tool_xyz"] is False


# ---- runner execution -------------------------------------------------------

def test_runner_dry_run_does_not_execute():
    r = CommandRunner(dry_run=True)
    res = r.run("echo hello")
    assert res.dry_run is True
    assert res.ok


def test_runner_real_execution_success():
    r = CommandRunner(dry_run=False)
    res = r.run("echo metamavs")
    assert res.dry_run is False
    assert res.returncode == 0
    assert "metamavs" in res.stdout


def test_runner_real_execution_failure_and_retry():
    r = CommandRunner(dry_run=False, retries=2)
    res = r.run("exit 3")
    assert res.returncode == 3
    assert res.attempts == 3  # 1 initial + 2 retries


# ---- maybe_execute_step ------------------------------------------------------

def test_step_dry_run_is_noop_and_falls_back():
    runner = make_runner(_state(dry_run=True))
    report, warnings, fell_back = maybe_execute_step(
        state=_state(dry_run=True), runner=runner, step="qc", commands=["echo x"], tools=["sh"]
    )
    assert report["mode"] == "dry_run"
    assert fell_back is True
    assert warnings == []


def test_step_graceful_fallback_when_tool_missing(tmp_path):
    runner = make_runner(_state(dry_run=False))
    report, warnings, fell_back = maybe_execute_step(
        state=_state(dry_run=False), runner=runner, step="detection",
        commands=["echo x"], tools=["definitely_not_a_real_tool_xyz"], log_dir=tmp_path,
    )
    assert report["mode"] == "fell_back"
    assert fell_back is True
    assert any("not installed" in w for w in warnings)


def test_step_executes_and_validates_outputs(tmp_path):
    out_file = tmp_path / "made.txt"
    runner = make_runner(_state(dry_run=False))
    report, warnings, fell_back = maybe_execute_step(
        state=_state(dry_run=False), runner=runner, step="qc",
        commands=[f"touch {out_file}"], tools=["touch"],
        expected_outputs=[out_file], log_dir=tmp_path,
    )
    assert report["mode"] == "executed"
    assert fell_back is False
    assert report["n_ok"] == 1
    assert report["outputs_ok"] is True
    assert out_file.exists()
    assert (tmp_path / "exec_qc.log").exists()


def test_step_warns_and_continues_on_command_failure(tmp_path):
    runner = make_runner(_state(dry_run=False))
    report, warnings, fell_back = maybe_execute_step(
        state=_state(dry_run=False), runner=runner, step="qc",
        commands=["sh -c 'exit 1'"], tools=["sh"], log_dir=tmp_path,
    )
    assert report["mode"] == "executed"
    assert report["n_failed"] == 1
    assert any("failed" in w for w in warnings)


def test_step_flags_missing_expected_output(tmp_path):
    runner = make_runner(_state(dry_run=False))
    report, warnings, fell_back = maybe_execute_step(
        state=_state(dry_run=False), runner=runner, step="qc",
        commands=["true"], tools=["true"],
        expected_outputs=[tmp_path / "never_created.txt"], log_dir=tmp_path,
    )
    assert report["outputs_ok"] is False
    assert any("expected output" in w for w in warnings)


# ---- end-to-end real (execute) mode with graceful fallback ------------------

def test_end_to_end_execute_mode_falls_back_and_completes(tmp_path):
    """In --execute mode with no bioinformatics tools installed, every tool
    step should fall back to synthetic data and the workflow should still
    complete and produce a report."""

    # Real files so input_manager (which requires existing files in real mode) passes.
    r1 = tmp_path / "s1_R1.fastq.gz"
    r2 = tmp_path / "s1_R2.fastq.gz"
    r1.write_text("")
    r2.write_text("")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        textwrap.dedent(
            f"""\
            sample_id,read1,read2,collection_date,location,sample_type
            s1,{r1},{r2},2026-01-01,site_A,wastewater
            s2,{r1},{r2},2026-01-08,site_A,wastewater
            """
        )
    )
    cfg_dict = {
        "project": {"name": "MetaMAVS", "run_name": "exec_test", "output_dir": str(tmp_path / "run")},
        "input": {"manifest": str(manifest), "sequencing_type": "paired_end"},
        "execution": {"dry_run": False, "mode": "local", "threads": 2},
    }
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg_dict))
    cfg = load_config(cfg_path)

    final = run_local_workflow(cfg, config_path=str(cfg_path), dry_run=False, run_id="run_exec_test")

    assert final["workflow_status"] in {"completed", "completed_with_warnings"}
    assert Path(final["markdown_report_path"]).exists()
    # Execution reports recorded; tool steps fell back (no tools installed).
    reports = final.get("execution_reports", [])
    assert reports, "expected execution_reports to be populated in execute mode"
    modes = {r["step"]: r["mode"] for r in reports}
    assert modes.get("qc") == "fell_back"
    assert modes.get("viral_detection") == "fell_back"


def test_slurm_script_generation(tmp_path):
    from metamavs.workflows.slurm_workflow import generate_slurm_script

    cfg_dict = {
        "project": {"run_name": "slurm_test", "output_dir": str(tmp_path / "run")},
        "input": {"manifest": "data/example_manifest.csv"},
        "slurm": {"partition": "gpu", "time": "12:00:00", "cpus_per_task": 16, "conda_env": "metamavs"},
    }
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg_dict))
    cfg = load_config(cfg_path)

    path = generate_slurm_script(cfg, str(cfg_path), dry_run=True)
    text = Path(path).read_text()
    assert "#SBATCH --partition=gpu" in text
    assert "--cpus-per-task=16" in text
    assert "conda activate metamavs" in text
    assert "metamavs run" in text and "--dry-run" in text
