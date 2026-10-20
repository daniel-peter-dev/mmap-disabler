# Changelog

## 0.1.1

- Package the extension as a ZIP-format JPL compatible with the tested official Android Jami release.
- Apply and read back the per-process `AAUDIO_POLICY_NEVER` policy at extension initialization.
- Preserve the policy until process exit when disabled/unloaded; document full app restart.
- Verified installation, automatic loading after app restart, non-MMAP audio paths and audible outgoing built-in-microphone speech on Galaxy S24 FE / Android 16 / Jami 20260925-01 (505).
- Public-source preparation adds portable host-tool lookup, standalone package auditing, regression tests, build instructions and a user guide. The phone-tested JPL is unchanged.

## 0.1.0 — superseded local prototype

- Initial native implementation and policy/loader probes.
- The original archive did not install successfully in the tested official app. The exact packaging failure was not conclusively identified. Use 0.1.1; the older artifact is not distributed here.
