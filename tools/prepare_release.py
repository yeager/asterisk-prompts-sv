#!/usr/bin/env python3
"""Create a verified release tree and manifest from a fully approved batch."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import wave
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", choices=("anton", "louise"), required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    ledger = json.loads((args.candidate_root / "generation-ledger.json").read_text(encoding="utf-8"))
    approval_blob = args.approval.read_bytes()
    approval = json.loads(approval_blob)
    if approval.get("voice") != args.voice or approval.get("approval_method") != "explicit_direct_human_statement":
        raise SystemExit("Approval record does not match the requested voice")
    approved = {(item.get("filename"), item.get("wav_sha256")): item for item in approval.get("items", [])}
    active = [entry for entry in ledger.get("entries", []) if entry.get("status") == "HUMAN_AUDIO_APPROVED_HASH_BOUND"]
    if len(active) != len(ledger.get("entries", [])) or len(approved) != len(active):
        raise SystemExit("Candidate batch is not completely and uniquely approved")
    items = []
    for entry in sorted(active, key=lambda item: item["filename"]):
        key = (entry["filename"], entry["wav_sha256"])
        if key not in approved:
            raise SystemExit(f"Missing hash-bound approval: {entry['filename']}")
        source = args.candidate_root.parents[1] / entry["candidate_audio_path"]
        if not source.is_file() or sha256(source) != entry["wav_sha256"]:
            raise SystemExit(f"Candidate hash changed: {entry['filename']}")
        with wave.open(str(source)) as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 48000, "NONE") or not audio.getnframes():
                raise SystemExit(f"Invalid WAV: {entry['filename']}")
        destination = args.release_root / entry["filename"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        items.append({"filename": entry["filename"], "wav_sha256": entry["wav_sha256"], "script": entry["script"]})
    write(args.manifest, {
        "format": "asterisk-prompts-sv-release-v1",
        "voice": args.voice,
        "source_approval": args.approval.name,
        "source_approval_sha256": hashlib.sha256(approval_blob).hexdigest(),
        "items": items,
    })
    print(f"Prepared {len(items)} verified files in {args.release_root}")


if __name__ == "__main__":
    main()
