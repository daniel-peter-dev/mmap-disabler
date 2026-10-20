# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the ARM64 extension, probes and a locally signed ZIP-format JPL."""
import datetime
import hashlib
import json
import os
import platform
import subprocess
import zipfile
from pathlib import Path

import msgpack
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = (
    'src/extension.cpp', 'src/mmap-policy.h', 'third_party/jami/jamiplugin.h',
    'manifest.json', 'assets/icon.png', 'tools/build.py', 'requirements-build.txt',
)


def signing_identity():
    private = ROOT / '.private'
    private.mkdir(mode=0o700, exist_ok=True)
    keyfile = private / 'extension.key'
    certfile = private / 'MmapDisabler.crt'
    if keyfile.exists() != certfile.exists():
        raise RuntimeError('Incomplete signing identity: restore the matching key/certificate pair in .private/')
    if keyfile.exists():
        key = serialization.load_pem_private_key(keyfile.read_bytes(), password=None)
        cert = x509.load_pem_x509_certificate(certfile.read_bytes())
    else:
        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Local MMAP extension prototype')])
        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                .public_key(key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - datetime.timedelta(days=1))
                .not_valid_after(now + datetime.timedelta(days=3650))
                .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                    key_encipherment=False, data_encipherment=False, key_agreement=False,
                    key_cert_sign=False, crl_sign=False, encipher_only=False, decipher_only=False), critical=True)
                .sign(key, hashes.SHA512()))
        # Exclusive creation; private key material never enters the archive or report.
        with keyfile.open('xb') as handle:
            keyfile.chmod(0o600)
            handle.write(key.private_bytes(serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        certfile.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    if not isinstance(key, rsa.RSAPrivateKey) or key.key_size < 3072:
        raise RuntimeError('Expected an RSA signing key of at least 3072 bits')
    if key.public_key().public_numbers() != cert.public_key().public_numbers():
        raise RuntimeError('Signing certificate/key mismatch')
    return key, cert, certfile.read_bytes()


def main():
    os.chdir(ROOT)
    configured = os.environ.get('ANDROID_NDK_HOME') or os.environ.get('ANDROID_NDK_ROOT')
    if not configured:
        raise SystemExit('Set ANDROID_NDK_HOME to an installed Android NDK r27d directory; see README.md.')
    ndk = Path(configured).expanduser().resolve()
    host = {'Windows': 'windows-x86_64', 'Linux': 'linux-x86_64', 'Darwin': 'darwin-x86_64'}.get(platform.system())
    if host is None:
        raise SystemExit('Unsupported host; use an NDK-supported Windows, Linux or macOS host.')
    toolbin = ndk / 'toolchains/llvm/prebuilt' / host / 'bin'
    windows = platform.system() == 'Windows'
    compiler = toolbin / ('aarch64-linux-android28-clang++' + ('.cmd' if windows else ''))
    nm = toolbin / ('llvm-nm' + ('.exe' if windows else ''))
    if not compiler.is_file() or not nm.is_file():
        raise SystemExit(f'Android ARM64 compiler/tools not found under {toolbin}; check ANDROID_NDK_HOME.')
    Path('build').mkdir(exist_ok=True)
    Path('dist').mkdir(exist_ok=True)
    flags = ['-std=c++17', '-Wall', '-Wextra', '-Werror']
    subprocess.run([str(compiler), *flags, '-fPIC', '-fvisibility=hidden', '-shared',
        '-Wl,-z,max-page-size=16384', '-Wl,--no-undefined', 'src/extension.cpp', '-ldl', '-llog',
        '-o', 'build/libMmapDisabler.so'], check=True)
    subprocess.run([str(compiler), *flags, 'tests/policy-test.cpp', '-o', 'build/policy-test'], check=True)
    subprocess.run([str(compiler), *flags, 'tests/loader-probe.cpp', '-ldl', '-o', 'build/loader-probe'], check=True)
    symbols = subprocess.check_output([str(nm), '-D', '--defined-only', 'build/libMmapDisabler.so'], text=True)
    if ' JAMI_dynPluginInit' not in symbols:
        raise RuntimeError('Missing Jami extension entry point')
    key, cert, certificate_pem = signing_identity()
    payload = {
        'manifest.json': Path('manifest.json').read_bytes(),
        'lib/arm64-v8a/libMmapDisabler.so': Path('build/libMmapDisabler.so').read_bytes(),
        'data/icon.png': Path('assets/icon.png').read_bytes(),
        'data/preferences.json': b'[]\n', 'data/accountpreferences.json': b'[]\n',
    }
    def sign(data):
        return key.sign(data, padding.PKCS1v15(), hashes.SHA512())
    signatures = msgpack.packb({name: sign(data) for name, data in sorted(payload.items())}, use_bin_type=True)
    payload.update({'signatures': signatures, 'signatures.sig': sign(signatures), 'MmapDisabler.crt': certificate_pem})
    artifact = Path('dist/MmapDisabler.jpl')
    with zipfile.ZipFile(artifact, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    report = {
        'artifact': artifact.as_posix(), 'bytes': artifact.stat().st_size,
        'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
        'certificateSha256': cert.fingerprint(hashes.SHA256()).hex(),
        'ndk': str(ndk), 'compiler': subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0],
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()},
        'sourceHashes': {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in SOURCE_FILES},
        'sourceHashMode': 'raw',
    }
    Path('build/build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('artifact', 'bytes', 'sha256', 'certificateSha256')}, indent=2))


if __name__ == '__main__':
    main()
