"""Command construction and execution.

Phase 1 used this purely to *build* and *log* commands. Phase 2 adds real
subprocess execution: tool-availability checks, exit-code capture, a simple
retry loop, and per-command logging. Dry-run mode is preserved unchanged --
when ``dry_run`` is True nothing is ever executed.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .logging_utils import get_logger

logger = get_logger("utils.command_runner")


@dataclass
class CommandResult:
    """Outcome of a (potentially simulated) command invocation."""

    command: str
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    dry_run: bool = True
    attempts: int = 1

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass
class CommandRunner:
    """Build and optionally execute shell commands.

    Parameters
    ----------
    dry_run:
        When True (the default) commands are recorded and logged but never run.
    threads:
        Default thread count made available to command builders.
    retries:
        Number of *additional* attempts for a failing command before giving up
        (0 = run once, no retry).
    """

    dry_run: bool = True
    threads: int = 8
    retries: int = 0
    history: list[str] = field(default_factory=list)

    def build(self, parts: list[str]) -> str:
        """Join *parts* into a single safely-quoted command string and record it."""

        cmd = " ".join(shlex.quote(str(p)) if " " in str(p) else str(p) for p in parts)
        self.history.append(cmd)
        return cmd

    @staticmethod
    def tool_available(tool: str) -> bool:
        """Return True if *tool* is found on the PATH (Phase 2 availability check)."""

        return shutil.which(tool) is not None

    def run(self, command: str, cwd: str | Path | None = None) -> CommandResult:
        """Execute *command* unless in dry-run mode.

        In dry-run mode the command is logged and a synthetic success result is
        returned. In real mode the command runs via :func:`subprocess.run`, with
        up to ``retries`` extra attempts if it exits non-zero.
        """

        if self.dry_run:
            logger.info("[dry-run] %s", command)
            return CommandResult(command=command, dry_run=True)

        last: CommandResult | None = None
        for attempt in range(1, self.retries + 2):
            logger.info("[exec%s] %s", f" try {attempt}" if self.retries else "", command)
            proc = subprocess.run(  # noqa: S602 - commands are constructed internally
                command,
                shell=True,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
            )
            last = CommandResult(
                command=command,
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                dry_run=False,
                attempts=attempt,
            )
            if last.ok:
                return last
            logger.warning("command exited %s (attempt %d): %s", last.returncode, attempt, command)
        return last  # type: ignore[return-value]
