import platform
import subprocess
import tempfile
import os


def print_pdf(payload: bytes, printer_cfg: dict):
    system = platform.system().lower()
    # write payload to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        if system in ("linux", "darwin"):
            cmd = ["lp", tmp_path]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode() or proc.stdout.decode() or "lp failed")
        elif system == "windows":
            # Use PowerShell to invoke default PDF handler
            cmd = [
                "powershell",
                "-Command",
                f"Start-Process -FilePath '{tmp_path}' -Verb Print"
            ]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.decode() or proc.stdout.decode() or "print failed")
        else:
            raise RuntimeError(f"Unsupported OS for PDF printing: {system}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
