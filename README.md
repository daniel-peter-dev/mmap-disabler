# Jami MMAP Disabler

**A small Android Jami extension that works around silent microphone capture on a tested Samsung Galaxy S24 FE by disabling AAudio MMAP inside Jami.**

Keep the official Jami app and your existing account. Install one `.jpl` extension, enable it, and restart Jami before making calls. No root or replacement APK is required.

This is an independent, experimental compatibility workaround, not an official Jami or Samsung release. It has been tested on one phone/software combination; it is not a general fix for every microphone problem.

[User guide](USER_GUIDE.md) · [Download the extension](dist/MmapDisabler.jpl?raw=true) · [Release metadata](dist/RELEASE.json) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

## The problem it addresses

On the tested phone, the built-in microphone worked in ordinary calls and recordings, but Jami sent silence. A Bluetooth headset worked. Separate mono/stereo tests pointed to the AAudio MMAP capture path: both channel configurations were silent with MMAP and produced audio when MMAP was disabled. The evidence does **not** establish a stereo-microphone defect or identify the underlying vendor/Android/Jami bug.

MMAP is a memory-mapped audio path that Android can use for low-latency AAudio streams. Android also provides a legacy path. This extension requests the latter inside Jami. See Android's [AAudio and MMAP documentation](https://source.android.com/docs/core/audio/aaudio).

## Install in brief

1. Download [`dist/MmapDisabler.jpl`](dist/MmapDisabler.jpl?raw=true) to your Android phone. Keep its `.jpl` filename.
2. End all calls. In **official Jami**, open **Settings → Advanced settings → Extensions → +** and select the file.
3. This package uses a self-signed certificate. On the tested Jami version, the supported **Force install** action permits a local extension. Use it only if you trust this package; it is not certified by the Jami Extension Store.
4. Enable **MmapDisabler** in Extensions.
5. Open Android **App info → Jami → Force stop**, then reopen Jami. Swiping it out of Recents is not a reliable substitute.
6. With Bluetooth disconnected, make a test call and ask the recipient whether your built-in microphone is audible.

The [user guide](USER_GUIDE.md) covers each step, updates, removal and troubleshooting. Jami documents its extension import screen [here](https://docs.jami.net/en_US/setup/jami-extensions-for-android.html). This extension loads at app startup; it is not a call-screen audio filter.

## Compatibility and evidence

| Item | Result |
| --- | --- |
| Extension | 0.1.1, ARM64 (`arm64-v8a`) |
| Phone | Samsung Galaxy S24 FE, SM-S721B |
| Android | 16 |
| Official Jami | Euclid 20260925-01, version code 505 |
| Installation | ZIP-format JPL installed using Jami's local-extension confirmation |
| Full app restart | Enabled extension automatically loaded after force stop and reopen |
| Audio path | Legacy, non-MMAP capture and playback observed in Android diagnostics |
| Built-in microphone | Recipient confirmed audible speech in an official-Jami call with Bluetooth disconnected |
| Local package checks | File/index signatures, ARM64 ELF, source/artifact hashes and two tamper controls pass |
| Native checks | Nine policy cases and an isolated Android loader probe passed during device testing |

**Not yet validated:** The removal/restoration procedure on the device. Other phones, Android releases and Jami versions are untested. Building for API 28 does not imply support for every Android 9+ device: extension loading and the dynamically resolved AAudio functions must also be available.

## How it works

`src/extension.cpp` exports Jami's `JAMI_dynPluginInit` entry point. On initialization it:

1. Checks the Jami plugin ABI.
2. Loads `libaaudio.so` and resolves `AAudio_getMMapPolicy` and `AAudio_setMMapPolicy`.
3. Requests policy `1` (`AAUDIO_POLICY_NEVER`) and verifies it by reading it back.
4. Reports initialization failure if the functions are unavailable or the policy cannot be applied.

The policy affects **new AAudio streams in Jami's process**, including capture and playback. It does not convert already-open streams, change global Android properties, or alter other apps. It may change audio latency or power use; this project has not measured those effects.

The extension registers no audio/video handlers and contains no recording, telemetry or network code. It is still native code loaded into Jami's process, so a package signature is an integrity check, not a sandbox or an endorsement.

The library retains its AAudio handle. Disabling or unloading the extension deliberately leaves the process policy in place until Jami exits, avoiding a policy change during a call. **After disabling or removing it, fully stop and reopen Jami.** No live restoration claim is made.

The helper returns `1` on success; failures are `-2` for unavailable functions, `-3` for an unreadable policy, `-4` for a rejected setter, and `-5` for a failed readback. On failed readback it attempts to restore the previous policy. Jami receives a null initialization result on failure.

## Verify the download

The checked-in package is the same package used in the successful phone test:

```text
Version:     0.1.1
Size:        23581 bytes
SHA-256:     ffe69d5739725854716c4e1e1dded4c9ad1279f5906836fab0d86654dffe5af0
Certificate: 21542a2892fc404320aebc3b090979e650ae82b415998a6764a214c4a06f3ce4
```

The certificate value is the SHA-256 fingerprint of its DER encoding, not the PEM file hash. [`dist/SHA256SUMS`](dist/SHA256SUMS) and [`dist/RELEASE.json`](dist/RELEASE.json) record public package/provenance information. Private signing material is not in the repository.

On Windows PowerShell:

```powershell
Get-FileHash .\dist\MmapDisabler.jpl -Algorithm SHA256
```

On Linux:

```bash
(cd dist && sha256sum -c SHA256SUMS)
```

Download the actual file, not GitHub's HTML preview. A checksum verifies that the file matches the metadata you obtained; it does not independently establish who published either file.

## Build from source

Ordinary users do not need these tools. Developers need Git, Python, the packages in `requirements-build.txt`, and an Android NDK installation. The tested build host is Windows x64 with Python 3.14 and NDK **r27d**. Host selection also supports the NDK's Linux and macOS layouts, but those builds have not been exercised here. No full Jami checkout or Android app rebuild is required.

### Windows PowerShell

Install Python and NDK r27d separately, then use your NDK's actual location:

```powershell
git clone https://github.com/daniel-peter-dev/mmap-disabler.git
cd mmap-disabler
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
$env:ANDROID_NDK_HOME = 'C:\Android\ndk\r27d'
.\.venv\Scripts\python.exe tools/build.py
.\.venv\Scripts\python.exe tools/audit.py --report build/build-report.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
```

### Linux / macOS host layout

The equivalent commands below are provided for developers; these host builds remain unverified:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
export ANDROID_NDK_HOME="$HOME/Android/ndk/r27d"
.venv/bin/python tools/build.py
.venv/bin/python tools/audit.py --report build/build-report.json
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

`ANDROID_NDK_ROOT` is accepted as a fallback. The target is `aarch64-linux-android28`; the library uses 16 KiB maximum ELF page alignment. The public Jami ABI header is vendored at the revision in [`source-lock.json`](source-lock.json).

Build outputs:

| Path | Purpose |
| --- | --- |
| `dist/MmapDisabler.jpl` | Installable ZIP-format extension; overwrites the local checked-in package when rebuilt |
| `build/libMmapDisabler.so` | ARM64 extension library |
| `build/policy-test` | Android executable for the nine policy cases |
| `build/loader-probe` | Android executable for isolated initialization checks |
| `build/build-report.json` | Local compiler, artifact, payload and source hashes |
| `.private/extension.key`, `.private/MmapDisabler.crt` | Local signing identity; keep private and backed up |

The first build generates a self-signed RSA-3072 identity. Later builds reuse the same pair. An incomplete or mismatched pair is rejected. A fresh checkout creates **your own identity**, not the maintainer's. Jami may reject an in-place update signed with a different identity; do not overwrite an existing trusted installation casually.

The generated private key is unencrypted and excluded by `.gitignore`. Keep the directory on protected storage and back up the pair securely. Only the public certificate is embedded in the JPL. Never commit the private key or local build report. See Jami's [certificate and signature format](https://docs.jami.net/en_US/extension/jami-extension-certificate.html).

Repeatable build steps are provided; byte-identical signed output across arbitrary hosts/toolchains is **not** promised. A new signing identity necessarily changes the JPL. Rebuilding with the tested Windows toolchain and original identity reproduced the phone-tested package exactly during this review. Local rebuilds do not regenerate `dist/RELEASE.json`; that metadata describes the published package, not your new build.

## Run checks without a phone

After installing the Python dependencies, audit the published package and its recorded source provenance:

```bash
python tools/audit.py --report dist/RELEASE.json
python -m unittest discover -s tests -p 'test_*.py' -v
```

Use your virtual environment's Python in those commands. For a local rebuild, use `--report build/build-report.json` instead. Without `--report`, the audit checks the package's internal signatures but does not bind it to a trusted release identity. The auditor uses explicit checks, not Python `assert` statements.

The pure C++ policy helper can also be tested with a host C++ compiler:

```bash
c++ -std=c++17 -Wall -Wextra -Werror tests/policy-test.cpp -o /tmp/mmap-policy-test
/tmp/mmap-policy-test
```

Exit code zero means all nine cases passed. Neither these tests nor a signed package prove microphone delivery in Jami; that requires a device call test.

## Optional Android developer probes

With USB debugging enabled and authorized, calls ended, and the Android executables built:

```bash
adb devices
python tools/check-device.py
```

Set `ADB` to the adb executable's path if it is not on `PATH`; use `--serial SERIAL` for an explicit device. The script copies only its three probe files to `/data/local/tmp/jami-mmap-extension-prototype`, runs in an isolated shell process, and writes `build/device-probe.json`. It opens no audio streams and does not install the extension or alter Jami. Shell-probe success does not prove compatibility inside the app.

The probe files remain on the phone. To remove that exact directory when finished:

```bash
adb shell rm -r /data/local/tmp/jami-mmap-extension-prototype
```

For extension logs, optionally use `adb logcat -s JamiMmapExtension`. Avoid posting full phone logs; the [contribution guide](CONTRIBUTING.md) describes a minimal report.

## Repository layout

```text
assets/          Extension icon
src/             Entry point and small policy helper
third_party/     Pinned Jami ABI header
tests/           Native probes and package-audit regression tests
tools/           Build, audit and optional isolated device checks
dist/            Current JPL, checksum and sanitized release metadata
USER_GUIDE.md    Install, test, update, disable and troubleshoot
COPYING          GNU GPL v3 license text
```

## License and credits

This project is licensed under **GPL-3.0-or-later**; see [COPYING](COPYING). The vendored Jami header retains Savoir-faire Linux's copyright and license notices. See [THIRD_PARTY.md](THIRD_PARTY.md) for provenance and dependency licenses. Jami, Android and Samsung names identify compatible software/devices; this project is not affiliated with their maintainers.
