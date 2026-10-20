# Third-party notices and provenance

## Jami plugin ABI header

`third_party/jami/jamiplugin.h` is an unmodified Jami daemon public plugin header, copyright 2004–2026 Savoir-faire Linux Inc., licensed under **GPL-3.0-or-later**. Its original notice is retained.

Pinned daemon revision: `1c057cc2163ee2e4eb9f5a49ea1a29224fb7c66d`.

[Upstream header](https://github.com/savoirfairelinux/jami-daemon/blob/1c057cc2163ee2e4eb9f5a49ea1a29224fb7c66d/src/plugin/jamiplugin.h).

The Android-client reference revision is `d7b7f0a23f65d2b336eb059dc1fc5c160cd93e71`; see `source-lock.json`. Neither the Jami app nor its account data is redistributed in this repository.

## Policy helper and icon

`src/mmap-policy.h` adapts the algorithm from the author's separate Jami Android MMAP experiment, under GPL-3.0-or-later. It is included in full here and requires no checkout of that project. `assets/icon.png` is a project-created icon distributed under the same license; it is not an official Jami logo.

## Build-time tools and dependencies

The Android NDK, Python and the Python packages are installed separately, not vendored or embedded in the JPL:

| Dependency | Version used | Upstream license |
| --- | --- | --- |
| Android NDK | r27d | Multiple component licenses; see the installed NDK notices |
| Python | 3.14 | Python Software Foundation License |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause |
| cffi | 2.1.1 | MIT-0 |
| pycparser | 3.11 | BSD-3-Clause |
| msgpack | 1.2.3 | Apache-2.0 |

`requirements-build.txt` records the tested Python dependency versions. These tools are not required on the user's phone. Android supplies `libaaudio`, `libdl` and `liblog` at runtime.

## Project license

Project source and documentation are provided under **GPL-3.0-or-later**. `COPYING` contains the GNU GPL version 3 text. This project is independently maintained and is not endorsed by Jami, Samsung or Google.
