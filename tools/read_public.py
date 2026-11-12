#!/usr/bin/env python3
"""Anonymous, GET-only reader for one pinned Ronen OS public snapshot."""
import argparse
import hashlib
import json
import re
import sys
import urllib.request

REPOSITORY = "RonenTitelbaum/RonenOS-Public"
BASE = "https://raw.githubusercontent.com/" + REPOSITORY
MAX_MANIFEST = 65536
MAX_DOCUMENT = 65536
DOCUMENTS = (
    "core/runtime.md", "modules/search.md", "modules/analysis.md",
    "workflows/pbs.md", "templates/handoff.md", "SETUP.txt", "policies/return_discount.json",
)
BASE_DOCUMENTS = ("core/runtime.md", "workflows/pbs.md", "templates/handoff.md")


class BundleError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BundleError("duplicate JSON key")
        result[key] = value
    return result


def parse_json(data):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise BundleError("invalid UTF-8 JSON") from exc


def validate_commit(commit):
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise BundleError("a full lowercase 40-character commit SHA is required")
    return commit


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get("schema") != "ronenos-public/v1":
        raise BundleError("unsupported manifest")
    if manifest.get("repository") != REPOSITORY or manifest.get("read_only") is not True:
        raise BundleError("unexpected repository or access mode")
    version = manifest.get("edition_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise BundleError("invalid edition version")
    files = manifest.get("documents")
    if not isinstance(files, list) or len(files) != len(DOCUMENTS):
        raise BundleError("unexpected document inventory")
    by_path = {}
    for item in files:
        if not isinstance(item, dict):
            raise BundleError("invalid document entry")
        path = item.get("path")
        if not isinstance(path, str) or path not in DOCUMENTS or path in by_path:
            raise BundleError("unapproved or duplicate document path")
        size, digest = item.get("bytes"), item.get("sha256")
        if type(size) is not int or not 0 <= size <= MAX_DOCUMENT:
            raise BundleError("invalid document size")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise BundleError("invalid document hash")
        by_path[path] = item
    if set(by_path) != set(DOCUMENTS):
        raise BundleError("missing required document")
    return by_path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BundleError("redirects are not allowed")


def fetch_bytes(url, limit):
    prefix = BASE + "/"
    if not url.startswith(prefix):
        raise BundleError("unapproved origin")
    tail = url[len(prefix):].split("/", 1)
    if len(tail) != 2:
        raise BundleError("invalid public URL")
    validate_commit(tail[0])
    if tail[1] not in (*DOCUMENTS, "PUBLIC_MANIFEST.json"):
        raise BundleError("unapproved URL path")
    request = urllib.request.Request(
        url, headers={"Accept": "text/plain", "User-Agent": "RonenOS-Public-Reader/1.0"},
        method="GET",
    )
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
        if response.geturl() != url:
            raise BundleError("unexpected response origin")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise BundleError("response size limit exceeded")
    return data


def load_bundle(commit, module="core", fetch=fetch_bytes):
    validate_commit(commit)
    if module not in ("core", "search", "analysis", "setup"):
        raise BundleError("unknown module")
    root = BASE + "/" + commit + "/"
    raw_manifest = fetch(root + "PUBLIC_MANIFEST.json", MAX_MANIFEST)
    if len(raw_manifest) > MAX_MANIFEST:
        raise BundleError("manifest size limit exceeded")
    manifest = parse_json(raw_manifest)
    inventory = validate_manifest(manifest)
    selected = list(BASE_DOCUMENTS)
    if module in ("search", "analysis"):
        selected.append("modules/search.md")
    if module == "analysis":
        selected.append("modules/analysis.md")
    if module == "setup":
        selected.extend(("SETUP.txt", "policies/return_discount.json"))
    frames = []
    for path in selected:
        expected = inventory[path]
        data = fetch(root + path, expected["bytes"])
        if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise BundleError("document integrity mismatch: " + path)
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise BundleError("document is not UTF-8") from exc
        frames.append((path, expected["sha256"], text))
    receipt = {
        "edition": "Ronen OS Public", "version": manifest["edition_version"],
        "mode": "ONLINE_PINNED", "repository": REPOSITORY,
        "commit": commit, "integrity": "VERIFIED_BYTES",
        "documents": selected, "access": "anonymous HTTPS GET; no GitHub credentials",
    }
    return json.dumps(receipt, ensure_ascii=False) + "\n\n" + "\n\n".join(
        "--- " + path + " SHA256=" + digest + " ---\n" + text
        for path, digest, text in frames
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--module", choices=("core", "search", "analysis", "setup"), default="core")
    args = parser.parse_args()
    try:
        output = load_bundle(args.commit, args.module)
    except Exception as exc:
        # Never print remote response bodies or partial unverified documents.
        print(json.dumps({"status": "BLOCKED", "error": type(exc).__name__}), file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
