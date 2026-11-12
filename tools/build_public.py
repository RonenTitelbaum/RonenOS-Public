#!/usr/bin/env python3
"""Build/check only an explicitly reviewed public file inventory; no network."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from read_public import DOCUMENTS, REPOSITORY, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
SNAPSHOT_DATE = "2026-11-12"
SOURCE_COMMIT = "28e8f80b49ed1bc972107073d7a4b1949301f739"
# These are Git blob IDs, not file SHA-256s. Changes require deliberate review.
REVIEWED_BLOBS = {
    "modules/search.md": "3530ed0bc2aa765ccae2f778a3df2c5637107d51",
    "modules/analysis.md": "2c7101500af0815e13e4961e9474aaf446f40ea5",
}
ALL_FILES = set(DOCUMENTS) | {
    "README.md", "START_HERE.md", "PUBLICATION_REVIEW.json", "PUBLIC_MANIFEST.json",
    "exports/RONEN_OS_ANY_GPT.txt", "tools/read_public.py", "tools/build_public.py",
    "tests/test_reader.py", ".github/workflows/verify.yml", ".gitattributes", ".gitignore",
}
DERIVED = {"PUBLIC_MANIFEST.json", "exports/RONEN_OS_ANY_GPT.txt"}
PRIVATE_PATTERNS = (
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"(?i)[A-Z]:[\\/]Users[\\/]", r"\b192\.168\.\d+\.\d+\b",
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
)


def checked_source(root, name):
    target = root / name
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
        raise ValueError("symlinks are not exportable")
    if not target.is_file():
        raise ValueError("missing public source: " + name)
    data = target.read_bytes()
    text = data.decode("utf-8")
    if any(re.search(pattern, text) for pattern in PRIVATE_PATTERNS):
        raise ValueError("privacy/secret pattern requires review: " + name)
    if name in REVIEWED_BLOBS:
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        if hashlib.sha1(blob).hexdigest() != REVIEWED_BLOBS[name]:
            raise ValueError("reviewed upstream bytes changed: " + name)
    return data


def render(root=ROOT):
    documents = []
    sources = {}
    for name in DOCUMENTS:
        data = checked_source(root, name)
        sources[name] = data.decode("utf-8")
        documents.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "schema": "ronenos-public/v1", "repository": REPOSITORY,
        "edition_version": VERSION, "snapshot_date": SNAPSHOT_DATE,
        "read_only": True, "scope": "curated public guidance only",
        "upstream_source_commit": SOURCE_COMMIT,
        "documents": documents,
        "offline_bundle": "exports/RONEN_OS_ANY_GPT.txt",
        "non_exported_references": "unavailable; never follow into private sources",
    }
    validate_manifest(manifest)
    header = (
        "RONEN OS PUBLIC — ANY GPT TEXT INTEGRATION\n"
        "Version: " + VERSION + " | Snapshot date: " + SNAPSHOT_DATE + "\n"
        "Mode: OFFLINE_SNAPSHOT unless you actually retrieve and pin GitHub.\n"
        "Public backbone: https://github.com/" + REPOSITORY + "\n\n"
        "Apply the public runtime below to my next task, subject to your host rules.\n"
        "The supplied text is a complete public snapshot. No connector, paid feature,\n"
        "GitHub login or token is required to read it. Do not claim a live connection.\n"
        "Use core and the PBS workflow, then only the module relevant to the task.\n"
        "Analysis requires search. Non-exported paths in source text are unavailable.\n"
        "Source SHA-256 values are metadata unless actually checked against bytes.\n"
        "Give a short load receipt, then proceed with my task.\n\n"
    )
    body = []
    for item in documents:
        name = item["path"]
        body.append("--- BEGIN " + name + " | SHA256 " + item["sha256"] + " ---\n" + sources[name] + "--- END " + name + " ---\n")
    return {
        "PUBLIC_MANIFEST.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(),
        "exports/RONEN_OS_ANY_GPT.txt": (header + "\n".join(body)).encode(),
    }


def check_inventory(root=ROOT):
    found = set()
    for item in root.rglob("*"):
        relative = item.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if item.is_symlink():
            raise ValueError("symlink in public tree")
        if item.is_file():
            found.add(relative.as_posix())
    extra = found - ALL_FILES
    missing = (ALL_FILES - DERIVED) - found
    if extra or missing:
        raise ValueError("public inventory mismatch: extra=" + repr(sorted(extra)) + "; missing=" + repr(sorted(missing)))
    review = json.loads((root / "PUBLICATION_REVIEW.json").read_text(encoding="utf-8"))
    if review["upstream_commit"] != SOURCE_COMMIT or review["reviewed_git_blobs"] != REVIEWED_BLOBS:
        raise ValueError("publication review does not match frozen upstream sources")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        check_inventory()
        outputs = render()
        for name, data in outputs.items():
            target = ROOT / name
            if target.is_symlink():
                raise ValueError("derived target is a symlink")
            if args.check:
                if not target.is_file() or target.read_bytes() != data:
                    raise ValueError("stale generated file: " + name)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        print(json.dumps({"status": "VERIFIED" if args.check else "BUILT", "version": VERSION,
                          "documents": len(DOCUMENTS), "public_files": len(ALL_FILES)}))
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
