#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class ApplicationE2EError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ApplicationE2EError(message)


def dist_digest() -> str:
    if not DIST.is_dir():
        fail("dist/ is missing; run the canonical build before application E2E")
    digest = hashlib.sha256()
    files = sorted(path for path in DIST.rglob("*") if path.is_file())
    if not files:
        fail("dist/ contains no files")
    for path in files:
        rel = path.relative_to(DIST).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def fetch(url: str, timeout: float = 2.0) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": "StudySyndicate-E2E/1"})
    with urlopen(request, timeout=timeout) as response:
        return int(response.status), response.read()


def run(port: int, receipt: Path | None) -> dict:
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        fail("npm executable not found")

    index_path = DIST / "index.html"
    if not index_path.is_file():
        fail("dist/index.html is missing; canonical build proof is required first")

    digest = dist_digest()
    base_url = f"http://127.0.0.1:{port}/"
    command = [npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(port), "--strictPort"]

    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.monotonic() + 20.0
        index_status = None
        index_body = b""
        while time.monotonic() < deadline:
            if process.poll() is not None:
                fail(f"npm run preview exited before readiness with code {process.returncode}")
            try:
                index_status, index_body = fetch(base_url)
                if index_status == 200:
                    break
            except Exception:
                time.sleep(0.25)
        else:
            fail("preview server did not become ready within 20 seconds")

        text = index_body.decode("utf-8", errors="replace")
        if 'id="root"' not in text:
            fail("served application index is missing the React root element")

        match = re.search(r'<script[^>]+src="([^"]+\.js)"', text)
        if not match:
            fail("served application index does not reference a built JavaScript asset")
        asset_url = urljoin(base_url, match.group(1))
        asset_status, asset_body = fetch(asset_url)
        if asset_status != 200 or not asset_body:
            fail("built JavaScript asset was not served successfully")

        payload = {
            "schema": "studysyndicate.application-e2e-receipt.v1",
            "entrypoint": command,
            "url": base_url,
            "indexStatus": index_status,
            "assetUrl": asset_url,
            "assetStatus": asset_status,
            "distSha256": digest,
            "proof": "real Vite preview HTTP path served the built index and referenced JavaScript asset",
            "browserInteraction": "not-proven-at-this-floor",
        }
        if receipt:
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise the built StudySyndicate app through its real Vite preview HTTP entrypoint.")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    payload = run(args.port, args.receipt)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ApplicationE2EError, OSError, subprocess.SubprocessError) as exc:
        print(f"application E2E FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
