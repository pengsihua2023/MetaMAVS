"""End-to-end Phase 3 test: hpc mode with MockBackend + fixtures, no real SSH."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from metamavs.config import load_config
from metamavs.workflows.local_workflow import run_local_workflow

FIX = Path(__file__).parent / "fixtures"


def _hpc_config(tmp_path) -> Path:
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "sample_id,read1,read2,collection_date,location,sample_type\n"
        "s1,/scratch/s1_R1.fq.gz,/scratch/s1_R2.fq.gz,2026-01-01,site_A,wastewater\n"
        "s2,/scratch/s2_R1.fq.gz,/scratch/s2_R2.fq.gz,2026-01-08,site_A,wastewater\n"
    )
    cfg = {
        "project": {"name": "MetaMAVS", "run_name": "hpc_test", "output_dir": str(tmp_path / "run")},
        "input": {"manifest": str(manifest), "sequencing_type": "paired_end", "remote_data": True},
        "execution": {"dry_run": False, "mode": "hpc", "threads": 4},
        "hpc": {"backend": "mock", "remote_base": "~/mtest", "mock_fixtures_dir": str(FIX)},
    }
    p = tmp_path / "hpc.yaml"
    p.write_text(yaml.safe_dump(cfg))
    return p


def test_end_to_end_hpc_mode_with_mock_backend(tmp_path):
    cfg = load_config(_hpc_config(tmp_path))
    final = run_local_workflow(cfg, config_path="hpc.yaml", dry_run=False, run_id="run_hpc_test")

    # Workflow completed and produced a report.
    assert final["workflow_status"] in {"completed", "completed_with_warnings"}
    assert Path(final["markdown_report_path"]).exists()

    # Remote stage ran and all mock jobs succeeded.
    rer = final["remote_execution_result"]
    assert rer["all_ok"] is True
    assert rer["failed"] == []

    # Results were synced and parsed.
    assert final["synced_manifest"]["complete"] is True
    assert final["parse_results"], "expected parser results"

    # Tables come from REAL parsed fixture data (Bracken preferred).
    hits = pd.read_csv(final["raw_viral_hits_path"])
    assert "Influenza A virus" in set(hits["taxon_name"])
    assert hits[hits["taxon_name"] == "Influenza A virus"]["reads"].iloc[0] == 3600

    # QC parsed from FastQC fixture (passes thresholds).
    assert final["qc_pass_fail"]["s1"] == "pass"

    # Risk escalates (Influenza A virus / Norovirus are high-risk) -> review triggered.
    assert final["risk_summary"]["overall_risk"] in {"High", "Critical"}
    assert final["review_required"] is True


def test_hpc_gottcha2_zero_viral_hits(tmp_path):
    """A bacteria-only GOTTCHA2 result -> 0 viral hits; pipeline still completes
    (no synthetic fallback, no empty-CSV crash) with a negative signal."""
    fx = tmp_path / "fx"
    fx.mkdir()
    (fx / "gottcha2.tsv").write_text(
        "LEVEL\tNAME\tTAXID\tREAD_COUNT\n"
        "species\tJeotgalibaca porci\t1868793\t218087\n"      # bacterium only
    )
    (fx / "gottcha2.lineage.tsv").write_text(
        "8.36\tsuperkingdom\t2\tBacteria\tspecies\t1868793\tJeotgalibaca porci\n"
    )
    manifest = tmp_path / "m.csv"
    manifest.write_text("sample_id,read1,read2\ns1,/scratch/s1_R1.fq.gz,/scratch/s1_R2.fq.gz\n")
    cfg = {
        "project": {"run_name": "zv", "output_dir": str(tmp_path / "run")},
        "input": {"manifest": str(manifest), "sequencing_type": "paired_end", "remote_data": True},
        "execution": {"dry_run": False, "mode": "hpc", "threads": 2},
        "tools": {"viral_detection": {"tools": ["gottcha2"], "gottcha2_db": "/db/g2.species.fna"}},
        "hpc": {"backend": "mock", "remote_base": "~/m", "steps": ["gottcha2"],
                "mock_fixtures_dir": str(fx)},
    }
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(cfg))
    final = run_local_workflow(load_config(p), config_path="c.yaml", dry_run=False, run_id="run_zv")

    assert final["workflow_status"] in {"completed", "completed_with_warnings"}
    hits = pd.read_csv(final["raw_viral_hits_path"])   # header-only, readable
    assert len(hits) == 0                               # no synthetic fallback
    assert final["risk_summary"]["overall_risk"] == "Low"
    assert Path(final["markdown_report_path"]).exists()


def test_hpc_job_failure_degrades_gracefully(tmp_path):
    """If a remote job fails, the run still completes (warn-and-continue)."""
    cfg_path = _hpc_config(tmp_path)
    # Force the viral_detection job to FAIL via config (mock backend).
    data = yaml.safe_load(Path(cfg_path).read_text())
    data["hpc"]["mock_fail_jobs"] = ["kraken2"]  # detection job is per-tool now
    Path(cfg_path).write_text(yaml.safe_dump(data))
    cfg = load_config(cfg_path)

    final = run_local_workflow(cfg, config_path="hpc.yaml", dry_run=False, run_id="run_hpc_fail")

    assert final["workflow_status"] in {"completed", "completed_with_warnings"}
    assert "kraken2" in final["remote_execution_result"]["failed"]
    assert Path(final["markdown_report_path"]).exists()
