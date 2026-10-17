"""Build the submission archive and verify it in an isolated environment."""

import json
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "vehicle-price-estimation-api.zip"
ARCHIVE_ROOT = "vehicle-price-estimation-api"
EXCLUDED_PARTS = {
    ".git",
    ".idea",
    ".claude",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
}
REQUIRED_FILES = {
    "artifacts/metadata.json",
    "artifacts/model_pipeline.joblib",
    "pyproject.toml",
    "src/vehicle_price/main.py",
    "uv.lock",
}


def should_archive(path: Path) -> bool:
    """Return whether a repository file belongs in the submission archive."""
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and not path.is_symlink()
        and not EXCLUDED_PARTS.intersection(relative.parts)
        and not path.name.startswith(".env")
        and path.suffix != ".zip"
    )


def build_archive() -> None:
    """Create a self-contained archive from the current repository contents."""
    archived_files: set[str] = set()
    with ZipFile(ARCHIVE, "w", ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not should_archive(path):
                continue
            relative = path.relative_to(ROOT)
            archived_files.add(relative.as_posix())
            archive.write(path, Path(ARCHIVE_ROOT) / relative)

    missing = REQUIRED_FILES - archived_files
    if missing:
        ARCHIVE.unlink(missing_ok=True)
        raise RuntimeError(f"Archive is missing required files: {sorted(missing)}")


def available_port() -> int:
    """Reserve an ephemeral local port long enough to discover its number."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request_json(url: str, payload: dict | None = None) -> dict:
    """Send an HTTP request and decode its JSON response."""
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP status: {response.status}")
        return json.load(response)


def wait_until_ready(process: subprocess.Popen[str], url: str) -> dict:
    """Wait for the extracted application to report readiness."""
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"API exited during startup:\n{output}")
        try:
            return request_json(f"{url}/health")
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)
    process.terminate()
    output, _ = process.communicate(timeout=10)
    raise RuntimeError(f"API startup timed out:\n{output}")


def project_python(root: Path) -> Path:
    """Return the virtual environment interpreter for the current platform."""
    windows_python = root / ".venv" / "Scripts" / "python.exe"
    return (
        windows_python if windows_python.exists() else root / ".venv" / "bin" / "python"
    )


def verify_archive() -> None:
    """Install and exercise the archived application outside the repository."""
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required to verify the submission archive")

    with tempfile.TemporaryDirectory(prefix="vehicle-price-zip-") as temporary:
        with ZipFile(ARCHIVE) as archive:
            archive.extractall(temporary)
        extracted_root = Path(temporary) / ARCHIVE_ROOT

        subprocess.run(
            [uv, "sync", "--frozen", "--no-dev", "--python", "3.12"],
            cwd=extracted_root,
            check=True,
        )

        port = available_port()
        url = f"http://127.0.0.1:{port}"
        process = subprocess.Popen(
            [
                str(project_python(extracted_root)),
                "-m",
                "uvicorn",
                "vehicle_price.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=extracted_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            health = wait_until_ready(process, url)
            expected_version = json.loads(
                (extracted_root / "artifacts" / "metadata.json").read_text()
            )["model_version"]
            if health != {"status": "ok", "model_version": expected_version}:
                raise RuntimeError(f"Unexpected health response: {health}")

            prediction = request_json(
                f"{url}/predict",
                {
                    "marque": "bmw",
                    "date_first_circulation": "2018-03-01",
                    "km": 108946,
                    "gearbox": "auto",
                },
            )
            if prediction.get("model_version") != expected_version:
                raise RuntimeError(f"Unexpected prediction response: {prediction}")
            if not isinstance(prediction.get("predicted_price"), (int, float)):
                raise TypeError(f"Unexpected prediction response: {prediction}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()


if __name__ == "__main__":
    build_archive()
    verify_archive()
    print(f"ZIP smoke test passed: {ARCHIVE}")
