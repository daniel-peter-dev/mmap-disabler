# SPDX-License-Identifier: GPL-3.0-or-later
"""Regression tests for the actual distributable package's audit boundary."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('package_audit', ROOT / 'tools/audit.py')
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


class PackageAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.artifact = ROOT / 'dist/MmapDisabler.jpl'
        with zipfile.ZipFile(self.artifact) as archive:
            self.files = {n: archive.read(n) for n in archive.namelist()}

    def package(self, files, duplicate=None):
        path = self.folder / 'changed.jpl'
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)
            if duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    archive.writestr(duplicate, files[duplicate])
        return path

    def test_original_signed_package(self):
        with contextlib.redirect_stdout(io.StringIO()):
            audit_module.audit(self.artifact)

    def test_modified_manifest_rejected(self):
        self.files['manifest.json'] += b' '
        with self.assertRaises(InvalidSignature):
            audit_module.audit(self.package(self.files))

    def test_modified_signature_index_rejected(self):
        self.files['signatures'] += b'x'
        with self.assertRaises(InvalidSignature):
            audit_module.audit(self.package(self.files))

    def test_missing_member_rejected(self):
        del self.files['data/icon.png']
        with self.assertRaisesRegex(ValueError, 'Unexpected/missing'):
            audit_module.audit(self.package(self.files))

    def test_extra_member_rejected(self):
        self.files['extra.txt'] = b'not in the approved package'
        with self.assertRaisesRegex(ValueError, 'Unexpected/missing'):
            audit_module.audit(self.package(self.files))

    def test_duplicate_member_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            audit_module.audit(self.package(self.files, duplicate='manifest.json'))

    def test_wrong_trusted_certificate_rejected(self):
        import hashlib
        report = {'sha256': hashlib.sha256(self.artifact.read_bytes()).hexdigest(),
                  'certificateSha256': '0' * 64}
        path = self.folder / 'report.json'
        path.write_text(json.dumps(report), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Certificate fingerprint mismatch'):
            audit_module.audit(self.artifact, path)


if __name__ == '__main__':
    unittest.main()
