"""Synthetic AGQ overflow probe tests (grid 71ec4ccc). No personal data, stdlib only, no network."""
import hashlib
import json
import os
import tempfile
import unittest


class ProbeTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(sum(range(101)), 5050)

    def test_sha256_known_vector(self):
        self.assertEqual(hashlib.sha256(b"abc").hexdigest(),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_json_roundtrip(self):
        doc = {"a": [1, 2, 3], "b": {"c": None}}
        self.assertEqual(json.loads(json.dumps(doc)), doc)

    def test_cpu_visible(self):
        self.assertGreaterEqual(os.cpu_count() or 0, 1)

    def test_tmp_write(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.txt")
            with open(p, "w") as f:
                f.write("probe\n")
            with open(p) as f:
                self.assertEqual(f.read(), "probe\n")
