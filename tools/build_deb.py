#!/usr/bin/env python3
"""Build a deterministic Debian package from a verified Asterisk sound tree."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import tarfile
import tempfile
import wave
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_directory(source: Path, destination: Path, members: list[Path]) -> None:
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(mode="w", fileobj=zipped, format=tarfile.GNU_FORMAT) as archive:
                for member in members:
                    info = archive.gettarinfo(str(source / member), arcname=member.as_posix())
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    info.mtime = 0
                    with (source / member).open("rb") as stream:
                        archive.addfile(info, stream)


def write_ar_archive(destination: Path, members: list[Path]) -> None:
    """Write the small, plain ar archive format required by Debian packages."""
    with destination.open("wb") as archive:
        archive.write(b"!<arch>\n")
        for member in members:
            name = member.name.encode("ascii")
            if len(name) > 15:
                raise ValueError(f"ar member name is too long: {member.name}")
            content = member.read_bytes()
            header = (
                name + b"/"
            ).ljust(16, b" ") + b"0".ljust(12, b" ") + b"0".ljust(6, b" ") + b"0".ljust(6, b" ") + b"100644".ljust(8, b" ") + str(len(content)).encode("ascii").ljust(10, b" ") + b"`\n"
            archive.write(header)
            archive.write(content)
            if len(content) % 2:
                archive.write(b"\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", choices=("anton", "louise"), required=True)
    parser.add_argument("--source", type=Path, required=True, help="Verified WAV source tree.")
    parser.add_argument("--manifest", type=Path, required=True, help="Hash-bound release manifest.")
    parser.add_argument("--output", type=Path, required=True, help="Target .deb path.")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--install-root", default="usr/share/asterisk/sounds/sv")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    items = manifest.get("items")
    if manifest.get("voice") != args.voice or not isinstance(items, list) or not items:
        raise SystemExit("Release manifest does not match the requested voice")
    expected: dict[str, str] = {}
    for item in items:
        filename, digest = item.get("filename"), item.get("wav_sha256")
        if not isinstance(filename, str) or not isinstance(digest, str):
            raise SystemExit("Malformed release manifest item")
        relative = Path(filename)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".wav":
            raise SystemExit(f"Unsafe release filename: {filename!r}")
        if filename in expected:
            raise SystemExit(f"Duplicate release filename: {filename}")
        expected[filename] = digest

    found = {path.relative_to(args.source).as_posix() for path in args.source.rglob("*.wav")}
    if found != set(expected):
        missing, extra = sorted(set(expected) - found), sorted(found - set(expected))
        raise SystemExit(f"Wrong file map: missing={missing[:3]}, extra={extra[:3]}")
    for filename, digest in expected.items():
        path = args.source / filename
        if sha256(path) != digest:
            raise SystemExit(f"Hash mismatch: {filename}")
        with wave.open(str(path)) as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 48000, "NONE") or not audio.getnframes():
                raise SystemExit(f"Invalid WAV: {filename}")

    package = f"asterisk-prompt-sv-{args.voice}"
    control = "\n".join((
        f"Package: {package}",
        f"Version: {args.version}",
        "Section: sound",
        "Priority: optional",
        "Architecture: all",
        "Maintainer: Daniel Nylander <danielnylander@users.noreply.github.com>",
        "Homepage: https://github.com/yeager/asterisk-prompts-sv",
        "License: CC-BY-SA-3.0",
        f"Description: Swedish Asterisk and FreePBX prompts, {args.voice} voice",
        "",
    )).encode("utf-8")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="asterisk-prompts-deb-") as temporary:
        root = Path(temporary)
        (root / "debian-binary").write_text("2.0\n", encoding="ascii")
        control_root = root / "control"
        control_root.mkdir()
        (control_root / "control").write_bytes(control)
        archive_directory(control_root, root / "control.tar.gz", [Path("control")])
        data_root = root / "data" / args.install_root
        data_root.mkdir(parents=True)
        for filename in expected:
            destination = data_root / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.source / filename, destination)
        archive_directory(root / "data", root / "data.tar.gz", [Path(args.install_root) / name for name in sorted(expected)])
        write_ar_archive(args.output, [root / "debian-binary", root / "control.tar.gz", root / "data.tar.gz"])
    print(f"Created {args.output} with {len(expected)} verified WAV files")


if __name__ == "__main__":
    main()
