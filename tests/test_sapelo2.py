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


def test_gottcha2_viral_lineage_filter(tmp_path):
    """With a sibling lineage.tsv, GOTTCHA2 parsing keeps only viral-superkingdom
    species (bacteria/archaea dropped)."""
    summary = tmp_path / "s1.gottcha2.tsv"
    summary.write_text(
        "LEVEL\tNAME\tTAXID\tREAD_COUNT\n"
        "species\tJeotgalibaca porci\t1868793\t218087\n"      # bacterium -> drop
        "species\tInfluenza A virus\t11320\t3400\n"            # virus -> keep
    )
    lineage = tmp_path / "s1.gottcha2.lineage.tsv"
    lineage.write_text(
        "8.36\tsuperkingdom\t2\tBacteria\tspecies\t1868793\tJeotgalibaca porci\n"
        "0.02\tsuperkingdom\t10239\tViruses\tspecies\t11320\tInfluenza A virus\n"
    )
    out = parse_gottcha2(str(summary), "s1")
    names = {r["taxon_name"] for r in out["records"]}
    assert names == {"Influenza A virus"}           # bacterium filtered out


def test_gottcha2_no_lineage_keeps_all_and_warns(tmp_path):
    summary = tmp_path / "s1.gottcha2.tsv"
    summary.write_text("LEVEL\tNAME\tTAXID\tREAD_COUNT\nspecies\tInfluenza A virus\t11320\t3400\n")
    out = parse_gottcha2(str(summary), "s1")
    assert {r["taxon_name"] for r in out["records"]} == {"Influenza A virus"}
    assert any("lineage" in w for w in out["result"].warnings)


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
    state["config"]["hpc"]["step_env"] = {
        "kraken2": ["export PATH=/envs/kraken2_env/bin:$PATH"],
        "gottcha2": ["export PATH=/envs/gottcha2_env/bin:$PATH"],
    }
    specs = build_job_specs(state)
    names = {s.job_name for s in specs}
    # Kraken2 and GOTTCHA2 are now SEPARATE jobs (different conda envs).
    assert "kraken2" in names and "gottcha2" in names
    k2 = next(s for s in specs if s.job_name == "kraken2")
    g2 = next(s for s in specs if s.job_name == "gottcha2")
    assert "kraken2 --db /db/k2" in "\n".join(k2.payload)
    assert "gottcha2.py -i" in "\n".join(g2.payload) and "/db/g2" in "\n".join(g2.payload)
    assert any("gottcha2.tsv" in o for o in g2.output_files)
    # per-step env applied to the rendered script
    assert "kraken2_env/bin" in Path(k2.script_local).read_text()
    assert "gottcha2_env/bin" in Path(g2.script_local).read_text()


def test_jobgen_gottcha2_only(tmp_path):
    """hpc.steps=[gottcha2] -> a single GOTTCHA2 job reading the raw FASTQ."""
    run_dir = tmp_path / "run"
    (run_dir / "intermediate").mkdir(parents=True)
    (run_dir / "intermediate" / "validated_manifest.csv").write_text(
        "sample_id,read1,read2\nWW01,/scratch/WW01_R1.fq.gz,/scratch/WW01_R2.fq.gz\n"
    )
    state = {
        "run_id": "rid", "run_dir": str(run_dir),
        "validated_manifest_path": str(run_dir / "intermediate" / "validated_manifest.csv"),
        "config": {"execution": {"threads": 8},
                   "hpc": {"remote_base": "/scratch/u/mm", "partition": "bahl_p", "steps": ["gottcha2"],
                           "step_env": {"gottcha2": ["export PATH=/envs/gottcha2_env/bin:$PATH"]}},
                   "tools": {"viral_detection": {"tools": ["gottcha2"], "gottcha2_db": "/db/g2.species"}}},
    }
    from metamavs.remote.jobgen import build_job_specs as bjs
    specs = bjs(state)
    assert [s.job_name for s in specs] == ["gottcha2"]
    g2 = specs[0]
    assert g2.depends_on == []                       # no host removal -> no deps
    # reads the RAW manifest paths (not host-removed work paths)
    assert "/scratch/WW01_R1.fq.gz" in "\n".join(g2.payload)


def test_sapelo2_config_loads():
    cfg = load_config("configs/sapelo2_config.yaml")
    assert cfg.hpc.host == "sapelo2.gacrc.uga.edu"
    assert cfg.hpc.partition == "bahl_p"
    assert cfg.execution.mode == "hpc"
    assert "gottcha2" in cfg.tools.viral_detection.tools
    assert cfg.hpc.ssh_control is True
