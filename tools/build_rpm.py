#!/usr/bin/env python3
"""Build a noarch RPM from a verified Asterisk sound tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
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
    parser.add_argument("--version", default="0.1.0")
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
    if shutil.which("rpmbuild") is None:
        raise SystemExit("rpmbuild is required to build an RPM")

    name = f"asterisk-prompt-sv-{args.voice}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="asterisk-prompts-rpm-") as temporary:
        topdir = Path(temporary)
        source_dir = topdir / "SOURCES" / "sounds"
        source_dir.mkdir(parents=True)
        for filename in expected:
            target = source_dir / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.source / filename, target)
        source_tar = topdir / "SOURCES" / "sounds.tar.gz"
        with tarfile.open(source_tar, "w:gz", format=tarfile.GNU_FORMAT) as archive:
            for filename in sorted(expected):
                info = archive.gettarinfo(str(source_dir / filename), arcname=f"sounds/{filename}")
                info.uid = info.gid = 0
                info.uname = info.gname = "root"
                info.mtime = 0
                with (source_dir / filename).open("rb") as stream:
                    archive.addfile(info, stream)
        spec = "\n".join((
            f"Name: {name}", f"Version: {args.version}", "Release: 1%{?dist}",
            "Summary: Swedish Asterisk and FreePBX prompts", "License: CC-BY-SA-3.0",
            "BuildArch: noarch", "Source0: sounds.tar.gz", "", "%description",
            f"Swedish Asterisk and FreePBX prompts, {args.voice} voice.", "", "%prep", "%setup -q -c -T", "tar -xzf %{SOURCE0}", "", "%install",
            "mkdir -p %{buildroot}/usr/share/asterisk/sounds/sv",
            "cp -a sounds/. %{buildroot}/usr/share/asterisk/sounds/sv/", "", "%files",
            "/usr/share/asterisk/sounds/sv", "",
        ))
        specs = topdir / "SPECS"; specs.mkdir()
        spec_path = specs / f"{name}.spec"; spec_path.write_text(spec, encoding="utf-8")
        subprocess.run(["rpmbuild", "-bb", str(spec_path), "--define", f"_topdir {topdir}"], check=True)
        built = next((topdir / "RPMS").rglob(f"{name}-{args.version}-*.noarch.rpm"))
        shutil.copyfile(built, args.output)
    print(f"Created {args.output} with {len(expected)} verified WAV files")


if __name__ == "__main__":
    main()
