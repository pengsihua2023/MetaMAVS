"""Build the remote SLURM job DAG.

Step-driven and per-step environment aware: each tool can live in its own conda
env / module set (resolved from ``hpc.step_env``), so e.g. Kraken2 and GOTTCHA2
become separate SLURM jobs. ``hpc.steps`` selects which steps to run (default:
derived from the tools config), enabling minimal runs like GOTTCHA2-only.

Activation is done by prepending the env's bin to PATH (robust on GACRC Sapelo2;
no ``conda init`` needed) -- supply those lines via ``hpc.step_env``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ..utils.file_utils import write_text
from .types import RemoteJobSpec, ResourceSpec


def _fastqc_base(read_path: str) -> str:
    """FastQC's output prefix for an input read file.

    FastQC strips a trailing ``.gz`` then a known sequence extension and appends
    ``_fastqc`` (e.g. ``sample_72_0_01.fq.gz`` -> ``sample_72_0_01_fastqc``).
    """

    name = Path(read_path).name
    if name.endswith(".gz"):
        name = name[:-3]
    for ext in (".fastq", ".fq", ".fasta", ".fa", ".bam", ".sam"):
        if name.endswith(ext):
            name = name[: -len(ext)]
            break
    return f"{name}_fastqc"


def _samples(state: dict) -> list[dict[str, Any]]:
    path = state.get("validated_manifest_path")
    if not path or not Path(path).exists():
        return []
    return pd.read_csv(path, dtype=str).fillna("").to_dict(orient="records")


def remote_run_dir(state: dict) -> str:
    hpc = state.get("config", {}).get("hpc", {}) or {}
    base = hpc.get("remote_base", "~/metamavs_runs")
    return f"{base}/metamavs/{state['run_id']}"


def _default_steps(tools_cfg: dict) -> list[str]:
    qc = tools_cfg.get("qc", {}) or {}
    vd_tools = [t.lower() for t in (tools_cfg.get("viral_detection", {}) or {}).get("tools", [])]
    nv = tools_cfg.get("novel_virus_screening", {}) or {}
    steps: list[str] = []
    if any(qc.get(t, False) for t in ("fastqc", "fastp", "multiqc")):
        steps.append("qc")
    steps.append("host_removal")
    if "kraken2" in vd_tools:
        steps.append("kraken2")
    if "gottcha2" in vd_tools:
        steps.append("gottcha2")
    if nv.get("enabled", True):
        steps.append("novel_virus")
    return steps


def build_job_specs(state: dict) -> list[RemoteJobSpec]:
    """Construct per-step job specs (writing their SLURM scripts locally)."""

    from .slurm import render_job_script

    cfg = state.get("config", {}) or {}
    hpc = cfg.get("hpc", {}) or {}
    tools_cfg = cfg.get("tools", {}) or {}
    run_dir = Path(state["run_dir"])
    rrun = remote_run_dir(state)
    threads = cfg.get("execution", {}).get("threads", 8)
    partition = hpc.get("partition", "batch")
    base_res = dict(partition=partition, cpus=hpc.get("cpus", 8),
                    mem=hpc.get("mem", "32G"), time=hpc.get("time", "24:00:00"))
    step_resources: dict[str, dict] = hpc.get("step_resources", {}) or {}
    scripts_local = run_dir / "remote" / "scripts"
    log_dir = f"{rrun}/logs"

    def res_for(step: str) -> ResourceSpec:
        return ResourceSpec(**{**base_res, "partition": partition, **step_resources.get(step, {})})

    step_env: dict[str, list[str]] = hpc.get("step_env", {}) or {}
    global_setup: list[str] = hpc.get("env_setup", [])
    conda_env = hpc.get("conda_env")
    steps = hpc.get("steps") or _default_steps(tools_cfg)
    host_enabled = "host_removal" in steps
    samples = _samples(state)
    specs: list[RemoteJobSpec] = []

    def env_for(step: str) -> list[str]:
        return step_env.get(step, global_setup)

    def reads_for(s: dict) -> tuple[str, str]:
        """Remote read paths for a sample: host-removed if that step runs, else raw."""
        sid = s["sample_id"]
        if host_enabled:
            return (f"{rrun}/work/{sid}_nonhost_R1.fastq.gz", f"{rrun}/work/{sid}_nonhost_R2.fastq.gz")
        return (s.get("read1", ""), s.get("read2", ""))

    def add(job_name: str, step: str, payload: list[str], outputs: list[str], deps: list[str]) -> None:
        spec = RemoteJobSpec(
            job_name=job_name, step=step, payload=payload, output_files=outputs, depends_on=deps,
            script_local=str(scripts_local / f"{job_name}.sh"),
            script_remote=f"{rrun}/scripts/{job_name}.sh", resources=res_for(step),
            env_setup=env_for(step), conda_env=conda_env if not env_for(step) else None,
        )
        write_text(spec.script_local, render_job_script(spec, log_dir=log_dir))
        specs.append(spec)

    qc_dep = ["qc"] if "qc" in steps else []
    host_dep = ["host_removal"] if host_enabled else []

    # --- qc ---
    if "qc" in steps:
        out, cmds = [], [f"mkdir -p {rrun}/results/qc"]
        for s in samples:
            sid = s["sample_id"]
            r1, r2 = s.get("read1", ""), s.get("read2", "")
            # FastQC writes <readbase>_fastqc.zip / .html (NOT a bare fastqc_data.txt);
            # with --extract it also writes <readbase>_fastqc/fastqc_data.txt. Copy that
            # to {sid}.fastqc_data.txt so the parser (which derives sample id from the
            # filename before the first '.') picks up the real metrics.
            cmds.append(f"fastqc --extract -t {threads} -o {rrun}/results/qc {r1} {r2}".strip())
            cmds.append(f"cp {rrun}/results/qc/{_fastqc_base(r1)}/fastqc_data.txt "
                        f"{rrun}/results/qc/{sid}.fastqc_data.txt")
            out.append(f"{rrun}/results/qc/{sid}.fastqc_data.txt")
        add("qc", "qc", cmds, out, [])

    # --- host_removal (minimap2 + samtools flagstat) ---
    if host_enabled:
        hr = tools_cfg.get("host_removal", {})
        ref = hr.get("host_reference") or "$HOST_REF"
        out, cmds = [], [f"mkdir -p {rrun}/results/host_removal {rrun}/work"]
        for s in samples:
            sid, r1, r2 = s["sample_id"], s.get("read1", ""), s.get("read2", "")
            bam = f"{rrun}/work/{sid}.host.bam"
            cmds.append(f"minimap2 -ax sr -t {threads} {ref} {r1} {r2} | samtools view -bS - > {bam}")
            cmds.append(f"samtools flagstat {bam} > {rrun}/results/host_removal/{sid}.flagstat")
            out.append(f"{rrun}/results/host_removal/{sid}.flagstat")
        add("host_removal", "host_removal", cmds, out, qc_dep)

    # --- kraken2 + bracken ---
    if "kraken2" in steps:
        vd = tools_cfg.get("viral_detection", {})
        k2db = vd.get("kraken2_db") or "$KRAKEN2_DB"
        out, cmds = [], [f"mkdir -p {rrun}/results/viral_detection {rrun}/work"]
        for s in samples:
            sid = s["sample_id"]
            r1, r2 = reads_for(s)
            rep = f"{rrun}/results/viral_detection/{sid}.kraken2.report"
            cmds.append(f"kraken2 --db {k2db} --threads {threads} --report {rep} "
                        f"--output {rrun}/work/{sid}.k2.out --paired {r1} {r2}")
            cmds.append(f"bracken -d {k2db} -i {rep} -o {rrun}/results/viral_detection/{sid}.bracken -r 150 -l S")
            out += [rep, f"{rrun}/results/viral_detection/{sid}.bracken"]
        add("kraken2", "kraken2", cmds, out, host_dep)

    # --- gottcha2 ---
    if "gottcha2" in steps:
        vd = tools_cfg.get("viral_detection", {})
        g2db = vd.get("gottcha2_db") or "$GOTTCHA2_DB"
        g2level = vd.get("gottcha2_level", "species")
        out, cmds = [], [f"mkdir -p {rrun}/results/viral_detection {rrun}/work"]
        for s in samples:
            sid = s["sample_id"]
            r1, r2 = reads_for(s)
            g2out = f"{rrun}/results/viral_detection/{sid}.gottcha2.tsv"
            g2lin = f"{rrun}/results/viral_detection/{sid}.gottcha2.lineage.tsv"
            cmds.append(f"gottcha2.py -i {r1} {r2} -d {g2db} -l {g2level} -t {threads} "
                        f"-o {rrun}/work/{sid}.gottcha2 -p {sid}")
            cmds.append(f"cp {rrun}/work/{sid}.gottcha2/{sid}.tsv {g2out}")
            # lineage table -> used downstream to keep only viral-superkingdom taxa
            cmds.append(f"cp {rrun}/work/{sid}.gottcha2/{sid}.lineage.tsv {g2lin}")
            out += [g2out, g2lin]
        add("gottcha2", "gottcha2", cmds, out, host_dep)

    # --- novel_virus (assembly + checkv) ---
    if "novel_virus" in steps:
        out, cmds = [], [f"mkdir -p {rrun}/results/novel_virus {rrun}/work"]
        for s in samples:
            sid = s["sample_id"]
            r1, r2 = reads_for(s)
            cmds.append(f"megahit -1 {r1} -2 {r2} -o {rrun}/work/{sid}.assembly")
            cmds.append(f"checkv end_to_end {rrun}/work/{sid}.assembly/final.contigs.fa {rrun}/work/{sid}.checkv")
            cmds.append(f"cp {rrun}/work/{sid}.checkv/quality_summary.tsv "
                        f"{rrun}/results/novel_virus/{sid}.checkv_quality_summary.tsv")
            out.append(f"{rrun}/results/novel_virus/{sid}.checkv_quality_summary.tsv")
        add("novel_virus", "novel_virus", cmds, out, host_dep)

    return specs
