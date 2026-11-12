import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import read_public as reader
import build_public as builder

COMMIT = "a" * 40


class PublicReaderTests(unittest.TestCase):
    def setUp(self):
        self.outputs = builder.render()
        self.manifest = json.loads(self.outputs["PUBLIC_MANIFEST.json"])
        self.calls = []

    def fetch(self, url, limit):
        self.calls.append((url, limit))
        prefix = reader.BASE + "/" + COMMIT + "/"
        self.assertTrue(url.startswith(prefix))
        name = url[len(prefix):]
        if name == "PUBLIC_MANIFEST.json":
            return json.dumps(self.manifest).encode()
        return (ROOT / name).read_bytes()

    def test_core_load_is_pinned_and_excludes_optional_modules(self):
        text = reader.load_bundle(COMMIT, fetch=self.fetch)
        receipt = json.loads(text.splitlines()[0])
        self.assertEqual(receipt["integrity"], "VERIFIED_BYTES")
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(receipt["documents"], list(reader.BASE_DOCUMENTS))

    def test_analysis_includes_search_prerequisite(self):
        text = reader.load_bundle(COMMIT, "analysis", self.fetch)
        receipt = json.loads(text.splitlines()[0])
        self.assertIn("modules/search.md", receipt["documents"])
        self.assertIn("modules/analysis.md", receipt["documents"])

    def test_mutable_refs_rejected_before_network(self):
        for ref in ("main", "latest", "../main", "a" * 39, "A" * 40, None):
            with self.subTest(ref=ref), self.assertRaises(reader.BundleError):
                reader.load_bundle(ref, fetch=self.fetch)
        self.assertEqual(self.calls, [])

    def test_paths_and_duplicate_inventory_rejected(self):
        for path in ("../private", "/etc/passwd", "core\\runtime.md", "https://example.com/x", "core/runtime.md?x=1"):
            manifest = copy.deepcopy(self.manifest)
            manifest["documents"][0]["path"] = path
            with self.subTest(path=path), self.assertRaises(reader.BundleError):
                reader.validate_manifest(manifest)
        self.manifest["documents"][1] = self.manifest["documents"][0]
        with self.assertRaises(reader.BundleError):
            reader.validate_manifest(self.manifest)

    def test_private_repository_and_write_mode_rejected(self):
        for field, value in (("repository", "RonenTitelbaum/RonenOS"), ("read_only", False)):
            manifest = copy.deepcopy(self.manifest)
            manifest[field] = value
            with self.subTest(field=field), self.assertRaises(reader.BundleError):
                reader.validate_manifest(manifest)

    def test_tampered_bytes_rejected_without_returning_partial_bundle(self):
        def tampered(url, limit):
            data = self.fetch(url, limit)
            return data + b"x" if url.endswith("workflows/pbs.md") else data
        with self.assertRaisesRegex(reader.BundleError, "integrity mismatch"):
            reader.load_bundle(COMMIT, fetch=tampered)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(reader.BundleError):
            reader.parse_json(b'{"read_only":true,"read_only":false}')

    def test_excessive_sizes_and_missing_sources_rejected(self):
        for size in (-1, True, 65537, "12"):
            manifest = copy.deepcopy(self.manifest)
            manifest["documents"][0]["bytes"] = size
            with self.subTest(size=size), self.assertRaises(reader.BundleError):
                reader.validate_manifest(manifest)
        self.manifest["documents"].pop()
        with self.assertRaises(reader.BundleError):
            reader.validate_manifest(self.manifest)

    def test_only_fixed_get_requests_without_authorization(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def geturl(self): return url
            def read(self, size): return b"ok"
        class Opener:
            def open(self, req, timeout):
                self_req.append(req)
                return Response()
        self_req = []
        url = reader.BASE + "/" + COMMIT + "/core/runtime.md"
        with patch.object(urllib.request, "build_opener", return_value=Opener()):
            self.assertEqual(reader.fetch_bytes(url, 2), b"ok")
        request = self_req[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertNotIn("authorization", {key.lower() for key, _ in request.header_items()})
        for bad in ("https://example.com/x", reader.BASE + "/main/core/runtime.md", reader.BASE + "/" + COMMIT + "/../private"):
            with self.assertRaises(reader.BundleError): reader.fetch_bytes(bad, 2)

    def test_redirects_and_oversized_responses_rejected(self):
        with self.assertRaises(reader.BundleError):
            reader.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")
        def too_large(url, limit): return b"x" * (reader.MAX_MANIFEST + 1)
        with self.assertRaises(reader.BundleError):
            reader.load_bundle(COMMIT, fetch=too_large)

    def test_unreviewed_tree_file_blocks_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "private-notes.txt").write_text("private", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                builder.check_inventory(root)

    def test_changed_upstream_and_symlinks_block_export(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "modules").mkdir()
            (root / "modules/search.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "upstream bytes changed"):
                builder.checked_source(root, "modules/search.md")
            target = root / "link.md"
            try:
                target.symlink_to(root / "modules/search.md")
            except (OSError, NotImplementedError):
                return  # Windows may disallow symlink creation for this account.
            with self.assertRaisesRegex(ValueError, "symlink"):
                builder.checked_source(root, "link.md")


if __name__ == "__main__":
    unittest.main()
