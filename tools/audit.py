# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the JPL, its signatures, tamper controls and optional provenance."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import msgpack
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(artifact, report_path=None):
    with zipfile.ZipFile(artifact) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate archive members')
        require(not any(i.is_dir() or i.file_size > 16 * 1024 * 1024 for i in archive.infolist()), 'Invalid/oversized members')
        files = {name: archive.read(name) for name in names}
    manifest = json.loads(files['manifest.json'])
    require(manifest['id'] == 'MmapDisabler', 'Unexpected extension ID')
    certname = manifest['id'] + '.crt'
    expected = {'manifest.json', 'lib/arm64-v8a/libMmapDisabler.so', 'data/icon.png',
                'data/preferences.json', 'data/accountpreferences.json', 'signatures', 'signatures.sig', certname}
    require(set(files) == expected, 'Unexpected/missing archive member')
    cert = x509.load_pem_x509_certificate(files[certname])
    pub = cert.public_key()
    require(isinstance(pub, rsa.RSAPublicKey) and pub.key_size >= 3072, 'Unexpected signing key')
    def verify(data, signature):
        pub.verify(signature, data, padding.PKCS1v15(), hashes.SHA512())
    verify(files['signatures'], files['signatures.sig'])
    sigs = msgpack.unpackb(files['signatures'], raw=False)
    require(set(sigs) == expected - {'signatures', 'signatures.sig', certname}, 'Incomplete signature index')
    for name, signature in sigs.items():
        verify(files[name], signature)
    for data, signature in ((files['manifest.json'] + b' ', sigs['manifest.json']),
                            (files['signatures'], bytes([files['signatures.sig'][0] ^ 1]) + files['signatures.sig'][1:])):
        try:
            verify(data, signature)
        except InvalidSignature:
            pass
        else:
            raise ValueError('Tamper control accepted')
    lib = files['lib/arm64-v8a/libMmapDisabler.so']
    require(lib[:6] == b'\x7fELF\x02\x01' and int.from_bytes(lib[18:20], 'little') == 183, 'Not an ARM64 ELF library')
    require(all(b'PRIVATE KEY' not in data for data in files.values()), 'Private key text found in package')
    if report_path:
        report = json.loads(report_path.read_text(encoding='utf-8'))
        require(hashlib.sha256(artifact.read_bytes()).hexdigest() == report['sha256'], 'Artifact hash mismatch')
        require(cert.fingerprint(hashes.SHA256()).hex() == report['certificateSha256'], 'Certificate fingerprint mismatch')
        if 'bytes' in report:
            require(artifact.stat().st_size == report['bytes'], 'Artifact size mismatch')
        if 'files' in report:
            require({n: hashlib.sha256(d).hexdigest() for n, d in files.items()} == report['files'], 'Payload hash mismatch')
        mode = report.get('sourceHashMode', 'raw')
        require(mode in ('raw', 'normalized-lf'), 'Unknown source hash mode')
        for name, digest in report.get('sourceHashes', {}).items():
            path = (ROOT / name).resolve()
            require(path.is_relative_to(ROOT), 'Source path outside repository')
            content = path.read_bytes()
            if mode == 'normalized-lf':
                content = content.replace(b'\r\n', b'\n')
            require(hashlib.sha256(content).hexdigest() == digest, f'Source hash mismatch: {name}')
    print('PASS: exact package members, ARM64 ELF, file/index signatures and both tamper controls')
    if report_path:
        print('PASS: artifact/certificate hashes and recorded source provenance')
    else:
        print('No trusted release/build report supplied; self-signature alone does not establish publisher identity.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, default=ROOT / 'dist/MmapDisabler.jpl')
    parser.add_argument('--report', type=Path, help='Trusted release metadata or local build/build-report.json')
    args = parser.parse_args()
    audit(args.artifact, args.report)


if __name__ == '__main__':
    main()
