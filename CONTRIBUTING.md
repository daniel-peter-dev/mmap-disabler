# Contributing

This is a small experimental workaround. Focused bug reports and pull requests are welcome; device coverage and response times are not guaranteed.

## Useful reports

Include the phone model, Android build/version, exact Jami version and distribution, extension version, whether installation succeeded, and the result after a full app restart. State whether the failure involves the built-in microphone, Bluetooth or another route. Include concise reproduction steps and exact error text.

Compatibility reports should distinguish installation, app-restart autoload, outgoing speech, incoming speech, video, route changes and background ringing. A successful shell probe is not evidence that the extension loaded inside Jami.

Do not post account exports, signing keys, credentials, account/contact identifiers, recordings or full phone logs. If you use adb, filter to `JamiMmapExtension` and inspect the output before sharing it. Never test by interrupting another person's active call.

## Development

Follow the README build and audit instructions. For a change, run the pure C++ policy test, package-audit tests, and a fresh signed-package audit. Record which host and device checks you actually ran. Changes involving activation timing, policy selection or packaging need an official-app device test before claiming compatibility.

Keep the extension process-local. Avoid system properties, root requirements, app-data migrations, recordings, background services and unload-time audio-policy changes. Do not add private keys, local build reports, APK copies or device diagnostics to commits. A development build has your own signing identity; do not confuse it with the checked-in package.

GPL-3.0-or-later applies to project contributions. Retain existing copyright and license notices. Keep dependency changes and source pins explicit in `source-lock.json` and `THIRD_PARTY.md`.
