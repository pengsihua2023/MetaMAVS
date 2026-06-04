"""Tests for Sapelo2 / real-cluster hardening: GOTTCHA2 parser, conda env setup,
SSH ControlMaster options, jobgen with GOTTCHA2, and the Sapelo2 config."""

from __future__ import annotations

from pathlib import Path

from metamavs.config import load_config
from metamavs.parsers import parse_gottcha2
from metamavs.remote.backends import build_ssh_backend_opts
from metamavs.remote.jobgen import build_job_specs
from metamavs.remote.slurm import render_job_script
from metamavs.remote.types import RemoteJobSpec

FIX = Path(__file__).parent / "fixtures"


def test_parse_gottcha2_species_only():
    out = parse_gottcha2(str(FIX / "gottcha2.tsv"), "s1")
    assert out["result"].ok
    names = {r["taxon_name"] for r in out["records"]}
    assert "Influenza A virus" in names
    assert "Alphainfluenzavirus" not in names  # genus row excluded
    flu = next(r for r in out["records"] if r["taxon_name"] == "Influenza A virus")
    assert flu["reads"] == 3400
    assert flu["tool"] == "gottcha2"


def test_render_script_with_env_setup_and_conda():
    spec = RemoteJobSpec(
        job_name="qc", step="qc", script_local="/x.sh", script_remote="/r/x.sh",
        payload=["fastqc in.fq"], conda_env="/home/u/.conda/envs/gottcha2_env",
        env_setup=["ml Miniconda3"],
    )
    script = render_job_script(spec, "/r/logs")
    assert "ml Miniconda3" in script
    assert "conda activate /home/u/.conda/envs/gottcha2_env" in script
    # env_setup precedes conda activate
    assert script.index("ml Miniconda3") < script.index("conda activate")


def test_ssh_control_master_opts():
    opts = build_ssh_backend_opts({"ssh_control": True})
    joined = " ".join(opts)
    assert "ControlMaster=auto" in joined
    assert "ControlPersist=8h" in joined
    # disabled -> no control options
    assert build_ssh_backend_opts({"ssh_control": False}) == []


def test_jobgen_includes_gottcha2(tmp_path):
    # Build a minimal validated manifest + state for jobgen.
    run_dir = tmp_path / "run"
    (run_dir / "intermediate").mkdir(parents=True)
    (run_dir / "intermediate" / "validated_manifest.csv").write_text(
        "sample_id,read1,read2\ns1,/scratch/s1_R1.fq.gz,/scratch/s1_R2.fq.gz\n"
    )
    state = {
        "run_id": "rid",
        "run_dir": str(run_dir),
        "validated_manifest_path": str(run_dir / "intermediate" / "validated_manifest.csv"),
        "config": {
            "execution": {"threads": 8},
            "hpc": {"remote_base": "/scratch/u/mm", "partition": "bahl_p",
                    "conda_env": "/home/u/.conda/envs/gottcha2_env", "env_setup": ["ml Miniconda3"]},
            "tools": {"viral_detection": {"tools": ["kraken2", "gottcha2"],
                                          "kraken2_db": "/db/k2", "gottcha2_db": "/db/g2"},
                      "host_removal": {"tool": "bowtie2"},
                      "novel_virus_screening": {"enabled": False}},
        },
    }
    specs = build_job_specs(state)
    vd = next(s for s in specs if s.job_name == "viral_detection")
    payload = "\n".join(vd.payload)
    assert "kraken2 --db /db/k2" in payload
    assert "gottcha2.py -i" in payload and "/db/g2" in payload
    assert any("gottcha2.tsv" in o for o in vd.output_files)
    # conda env setup propagated to the rendered script
    assert "ml Miniconda3" in Path(vd.script_local).read_text()


def test_sapelo2_config_loads():
    cfg = load_config("configs/sapelo2_config.yaml")
    assert cfg.hpc.host == "sapelo2.gacrc.uga.edu"
    assert cfg.hpc.partition == "bahl_p"
    assert cfg.execution.mode == "hpc"
    assert "gottcha2" in cfg.tools.viral_detection.tools
    assert cfg.hpc.ssh_control is True
