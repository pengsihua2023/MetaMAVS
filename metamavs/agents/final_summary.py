"""final_summary_node: produce a concise end-of-run summary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..state import (
    MetaMAVSState,
    STATUS_COMPLETED,
    STATUS_COMPLETED_WITH_WARNINGS,
    STATUS_RUNNING,
)
from ..utils.file_utils import write_json
from ..utils.logging_utils import get_logger

logger = get_logger("agents.final_summary")


def final_summary_node(state: MetaMAVSState) -> dict[str, Any]:
    """Summarise the run: status, report paths, key risks and warnings."""

    logger.info("Building final run summary")
    run_dir = Path(state["run_dir"])

    errors = state.get("errors", []) or []
    warnings = state.get("warnings", []) or []
    risk = state.get("risk_summary", {}) or {}

    # Preserve any terminal status already set (e.g. failed by the error handler,
    # rejected_by_reviewer). Only the initial "running"/unset status is derived
    # here into completed / completed_with_warnings.
    status = state.get("workflow_status", "")
    if status in {"", STATUS_RUNNING}:
        status = STATUS_COMPLETED_WITH_WARNINGS if warnings else STATUS_COMPLETED

    high_risk = [
        r["taxon_name"]
        for r in risk.get("top_risks", [])
        if r.get("risk_level") in {"High", "Critical"}
    ]

    exec_reports = state.get("execution_reports", []) or []
    exec_modes = {r.get("step"): r.get("mode") for r in exec_reports}

    final_summary = {
        "status": status,
        "run_id": state.get("run_id", ""),
        "run_dir": str(run_dir),
        "overall_risk": risk.get("overall_risk", "Low"),
        "high_risk_detections": high_risk,
        "n_warnings": len(warnings),
        "n_errors": len(errors),
        "execution_modes": exec_modes,
        "markdown_report": state.get("markdown_report_path"),
        "html_report": state.get("html_report_path"),
        "review_decision": state.get("review_decision"),
    }

    # Persist the complete final state alongside the summary. Fold in this node's
    # own outputs (final_summary, resolved status) so the on-disk state.json
    # reflects the finished run rather than the pre-final_summary "running" state.
    serialized = {k: v for k, v in state.items() if k != "config"}
    serialized["config"] = state.get("config", {})
    serialized["final_summary"] = final_summary
    serialized["workflow_status"] = status
    write_json(run_dir / "state.json", serialized)
    write_json(run_dir / "logs" / "final_summary.json", final_summary)

    logger.info("Run %s complete: status=%s, overall_risk=%s", final_summary["run_id"], status, final_summary["overall_risk"])

    return {
        "final_summary": final_summary,
        "workflow_status": status,
        "execution_log": [f"final_summary: status={status}"],
    }
