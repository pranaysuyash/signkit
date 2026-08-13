"""Optional structural preflight for PDFs before native processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class PdfPreflightResult:
    """Bounded result from qpdf structural inspection."""

    available: bool
    status: str
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""

    @property
    def can_process(self) -> bool:
        """Return whether preflight did not report a structural error."""
        return self.status in {"clean", "warnings", "unavailable"}


def run_qpdf_check(
    pdf_path: str | Path,
    *,
    qpdf_executable: str | None = None,
    timeout_seconds: float = 10.0,
    suppress_recovery: bool = False,
) -> PdfPreflightResult:
    """Run qpdf ``--check`` when installed, without making it mandatory.

    qpdf is an early structural signal, not a PDFium sandbox or a complete
    PDF specification validator. Unavailability is explicit and non-blocking;
    callers handling untrusted documents can choose a policy that requires it.
    """

    executable = qpdf_executable or shutil.which("qpdf")
    if not executable:
        return PdfPreflightResult(False, "unavailable", None)

    command = [executable, "--check"]
    if suppress_recovery:
        command.append("--suppress-recovery")
    command.append(str(pdf_path))

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return PdfPreflightResult(True, "timeout", None, stderr=str(exc))
    except OSError as exc:
        return PdfPreflightResult(True, "unavailable", None, stderr=str(exc))

    if completed.returncode == 0:
        status = "clean"
    elif completed.returncode == 3:
        status = "warnings"
    elif completed.returncode == 2:
        status = "errors"
    else:
        status = "failed"
    return PdfPreflightResult(
        True,
        status,
        completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
