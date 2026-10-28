#!/usr/bin/env python3
"""Create a verified release tree from one or more approved candidate batches."""
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
    parser.add_argument("--approved-manus", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, action="append", required=True)
    parser.add_argument("--approval", type=Path, action="append", required=True)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    manuscript = json.loads(args.approved_manus.read_text(encoding="utf-8"))
    rows = manuscript.get("items")
    if manuscript.get("approved_count") != len(rows or []) or not isinstance(rows, list):
        raise SystemExit("Approved manuscript record is malformed")
    expected = {row.get("filename"): row for row in rows}
    if None in expected or len(expected) != len(rows):
        raise SystemExit("Approved manuscript filenames are malformed or duplicate")

    approvals: dict[tuple[str, str], dict] = {}
    approval_proof = []
    for approval_path in args.approval:
        blob = approval_path.read_bytes()
        record = json.loads(blob)
        if record.get("format") not in {"asterisk-prompt-se-anton-audio-approval-v1", "asterisk-prompt-se-audio-approval-v1"}:
            raise SystemExit(f"Unsupported approval record: {approval_path}")
        if record.get("voice") not in (None, args.voice):
            raise SystemExit(f"Approval record voice mismatch: {approval_path}")
        for item in record.get("items", []):
            key = (item.get("filename"), item.get("wav_sha256"))
            if not all(key) or key in approvals:
                raise SystemExit(f"Malformed or duplicate approval: {approval_path}")
            approvals[key] = item
        approval_proof.append({"path": str(approval_path), "sha256": hashlib.sha256(blob).hexdigest()})

    candidates: dict[tuple[str, str], tuple[dict, Path]] = {}
    for root in args.candidate_root:
        ledger = json.loads((root / "generation-ledger.json").read_text(encoding="utf-8"))
        workspace_root = next(
            parent for parent in (root.resolve(), *root.resolve().parents)
            if (parent / "outputs").is_dir()
        )
        for entry in ledger.get("entries", []):
            if entry.get("status") != "HUMAN_AUDIO_APPROVED_HASH_BOUND":
                continue
            key = (entry.get("filename"), entry.get("wav_sha256"))
            if not all(key) or key in candidates:
                raise SystemExit(f"Malformed or duplicate approved candidate: {root}")
            candidates[key] = (entry, workspace_root)

    approved_names = {name for name, _ in approvals}
    if approved_names != set(expected):
        missing = sorted(set(expected) - approved_names)
        extra = sorted(approved_names - set(expected))
        raise SystemExit(f"Approval coverage mismatch: missing={missing[:3]}, extra={extra[:3]}")

    items = []
    for filename, manuscript_row in sorted(expected.items()):
        approved = next(item for (name, _), item in approvals.items() if name == filename)
        key = (filename, approved["wav_sha256"])
        candidate = candidates.get(key)
        if candidate is None:
            raise SystemExit(f"No matching approved candidate: {filename}")
        entry, workspace_root = candidate
        if approved.get("script") != manuscript_row.get("script") or entry.get("script") != manuscript_row.get("script"):
            raise SystemExit(f"Script mismatch: {filename}")
        source = workspace_root / entry["candidate_audio_path"]
        if not source.is_file() or sha256(source) != approved["wav_sha256"]:
            raise SystemExit(f"Candidate hash changed: {filename}")
        with wave.open(str(source)) as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 48000, "NONE") or not audio.getnframes():
                raise SystemExit(f"Invalid WAV: {filename}")
        destination = args.release_root / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        items.append({"filename": filename, "wav_sha256": approved["wav_sha256"], "script": manuscript_row["script"]})
    write(args.manifest, {
        "format": "asterisk-prompts-sv-release-v1",
        "voice": args.voice,
        "approved_manus_sha256": sha256(args.approved_manus),
        "source_approvals": approval_proof,
        "items": items,
    })
    print(f"Prepared {len(items)} verified files in {args.release_root}")


if __name__ == "__main__":
    main()
