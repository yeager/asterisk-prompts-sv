#!/usr/bin/env python3
"""Build a deterministic tar.gz archive from a verified Asterisk sound tree."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
import wave
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", choices=("anton", "louise"), required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("voice") != args.voice or not isinstance(manifest.get("items"), list):
        raise SystemExit("Release manifest does not match the requested voice")
    expected: dict[str, str] = {}
    for item in manifest["items"]:
        filename, digest = item.get("filename"), item.get("wav_sha256")
        relative = Path(filename) if isinstance(filename, str) else None
        if not relative or relative.is_absolute() or ".." in relative.parts or relative.suffix != ".wav" or not isinstance(digest, str):
            raise SystemExit("Malformed release manifest item")
        if filename in expected:
            raise SystemExit(f"Duplicate release filename: {filename}")
        expected[filename] = digest
    found = {path.relative_to(args.source).as_posix() for path in args.source.rglob("*.wav")}
    if found != set(expected):
        raise SystemExit("Source file map does not match the release manifest")
    for filename, digest in expected.items():
        path = args.source / filename
        if sha256(path) != digest:
            raise SystemExit(f"Hash mismatch: {filename}")
        with wave.open(str(path)) as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 48000, "NONE") or not audio.getnframes():
                raise SystemExit(f"Invalid WAV: {filename}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(mode="w", fileobj=zipped, format=tarfile.GNU_FORMAT) as archive:
                for filename in sorted(expected):
                    path = args.source / filename
                    info = archive.gettarinfo(str(path), arcname=filename)
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = 0
                    with path.open("rb") as stream:
                        archive.addfile(info, stream)
    print(f"Created {args.output} with {len(expected)} verified WAV files")


if __name__ == "__main__":
    main()
