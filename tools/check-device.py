# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional isolated Android probes; no Jami installation, audio streams or calls."""
import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', help='Explicit adb device serial, if several devices are connected')
    args = parser.parse_args()
    adb = os.environ.get('ADB', 'adb')
    target = ['-s', args.serial] if args.serial else ['-d']
    def run(*arguments):
        result = subprocess.run([adb, *target, *arguments], text=True, capture_output=True, check=True)
        return result.stdout.strip()
    folder = '/data/local/tmp/jami-mmap-extension-prototype'
    run('shell', 'mkdir', '-p', folder)
    for name in ('policy-test', 'loader-probe', 'libMmapDisabler.so'):
        run('push', str(ROOT / 'build' / name), folder + '/' + name)
    run('shell', 'chmod', '700', folder + '/policy-test', folder + '/loader-probe')
    run('shell', folder + '/policy-test')
    probe = run('shell', folder + '/loader-probe', folder + '/libMmapDisabler.so')
    report = {'policyCases': 9, 'policyResult': 'passed', 'loaderProbe': probe,
              'scope': 'Isolated shell process only; no audio opened. This does not validate loading or calls in Jami.'}
    (ROOT / 'build/device-probe.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    print('Probe files remain in ' + folder + '; see README for optional cleanup.')


if __name__ == '__main__':
    main()
