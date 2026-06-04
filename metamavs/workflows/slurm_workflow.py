"""SLURM workflow backend (Phase 2: submission-script generation).

Generates an sbatch submission script from the config's ``slurm`` section. It
does not submit jobs (no ``sbatch`` call) -- submission/orchestration of
per-step dependent jobs is a later refinement. The generated script is safe to
review and run by hand on an HPC login node.
"""

from __future__ import annotations

from pathlib import Path

from ..config import MetaMAVSConfig
from ..utils.file_utils import ensure_run_dir, write_text
from ..utils.logging_utils import get_logger

logger = get_logger("workflows.slurm")


def _render_script(config: MetaMAVSConfig, config_path: str, run_dir: Path, dry_run: bool) -> str:
    s = config.slurm
    lines = [
        "#!/usr/bin/env bash",
        f"#SBATCH --job-name={config.project.run_name}",
        f"#SBATCH --partition={s.partition}",
        f"#SBATCH --cpus-per-task={s.cpus_per_task}",
        f"#SBATCH --mem={s.mem}",
        f"#SBATCH --time={s.time}",
        f"#SBATCH --output={run_dir}/logs/slurm_%j.out",
        f"#SBATCH --error={run_dir}/logs/slurm_%j.err",
        "",
        "set -euo pipefail",
        "",
    ]
    for mod in s.modules:
        lines.append(f"module load {mod}")
    if s.conda_env:
        lines.append(f"source activate {s.conda_env}  # or: conda activate {s.conda_env}")
    if s.modules or s.conda_env:
        lines.append("")

    flag = "--dry-run" if dry_run else "--execute"
    lines += [
        "# Run the MetaMAVS workflow. Remove --dry-run to execute real commands",
        "# once the required bioinformatics tools and databases are available.",
        f"metamavs run --config {config_path} {flag}",
        "",
    ]
    return "\n".join(lines)


def generate_slurm_script(config: MetaMAVSConfig, config_path: str, dry_run: bool = True) -> Path:
    """Write a SLURM submission script and return its path."""

    run_dir = ensure_run_dir(config.project.output_dir)
    script = _render_script(config, config_path, run_dir, dry_run)
    path = run_dir / "commands" / "submit_slurm.sh"
    write_text(path, script)
    logger.info("SLURM script written: %s", path)
    return path
