# User guide — Jami MMAP Disabler

This guide is for installing the extension in **official Jami on an Android phone**. You keep your existing Jami account. It is not a Raspberry Pi application or a replacement Jami APK.

## Is this for my problem?

The workaround was tested on a Samsung Galaxy S24 FE running Android 16 and Jami Euclid 20260925-01 (505). On that phone, Jami calls connected but the other person heard silence from its built-in microphone. Ordinary recordings worked and a Bluetooth headset worked in Jami.

The extension fixed that tested case. Other devices and versions may behave differently. If your microphone is muted, permission is denied, or Android's microphone access is off, correct those settings first.

You need official Android Jami with extension support, an ARM64 phone, and the `MmapDisabler.jpl` file. **No root, computer, USB debugging, Python or compiler is needed to install it.**

## 1. Download the file

1. Open this project's [repository](https://github.com/daniel-peter-dev/mmap-disabler) on your phone.
2. Follow the README's **Download the extension** link, or open `dist/MmapDisabler.jpl` and use GitHub's download button.
3. Save the file to **Downloads**. Its name should end in `.jpl`, not `.html`, `.apk` or `.zip`.

Use the actual download button if GitHub displays a preview. Do not extract or repackage the file. The [README](README.md#verify-the-download) provides a checksum for users who want to verify it.

## 2. Import into official Jami

1. End all active calls.
2. Open **official Jami**. If you also have a separate test build installed, make sure you are using the official app.
3. Open **Settings → Advanced settings → Extensions**.
4. Tap **+**, browse to **Downloads**, and select `MmapDisabler.jpl`.
5. On the tested version, Jami initially distrusts the package's self-signed certificate and offers **Force install**. This is Jami's supported confirmation for a locally signed extension. Use it only after deciding you trust this project and the downloaded file.
6. Confirm the extension is installed, then enable **MmapDisabler** in the Extensions screen. If Jami has a general extensions switch, enable that as well.

Menu wording and the confirmation's placement may vary by Jami version. If installation fails without that action, stop and follow the troubleshooting section; do not disable Android protections or install a different APK.

This extension changes the audio path when it loads. It does not add an effect or a button to the call screen, and there are no microphone recordings to configure.

## 3. Fully restart Jami

Do this with all calls ended:

1. Long-press Jami's app icon and choose **App info** (the information icon). Alternatively, open Android **Settings → Apps → Jami**.
2. Tap **Force stop** and confirm.
3. Reopen Jami from its icon.

Swiping the app away from Recents may leave its service running. A full force stop matters because existing audio streams cannot be converted while they are open.

After a force stop, reopen Jami so it can receive calls again. On the tested software, an enabled extension loaded automatically when Jami reopened. Whole-phone reboot behavior has not been validated separately.

## 4. Check that it works

1. Disconnect Bluetooth and unplug external headsets so the built-in microphone is used.
2. Call a second device or a person who can help.
3. Check that Jami's microphone is unmuted and Android microphone permission/access is allowed.
4. Speak normally and ask the recipient whether your voice is audible.
5. Ask the other person to speak too, and check that you can hear them.

Audible outgoing speech was confirmed in the original test. A full two-way checklist, video, changing audio routes during calls and locked-screen/background ringing still need separate testing. Please report what you actually tested rather than assuming every function is covered.

## Everyday use

Keep the extension enabled and use Jami normally. You do not need to activate it for each call. It changes the MMAP policy only inside Jami's process; other applications keep their own audio behavior.

The workaround affects newly created AAudio capture **and playback** streams. Possible latency or power differences have not been measured. If it causes problems, disable it and fully restart Jami as described below.

## Update the extension

1. End all calls and download the new `.jpl` from the same trusted project.
2. Check the release notes and compatibility information.
3. Import it from Jami's Extensions screen and follow the app's update/confirmation prompts.
4. Confirm it remains enabled, force stop Jami and reopen it.
5. Repeat the microphone check.

Packages built by another person may have a different signing identity. If Jami rejects an update or asks you to remove the old extension, verify the source before proceeding. This guide does not require deleting your Jami account or clearing app data.

## Disable or remove it

1. End all calls.
2. Open **Jami → Settings → Advanced settings → Extensions**.
3. Disable **MmapDisabler**, or uninstall it using its extension entry.
4. **Force stop Jami through Android App info and reopen it.**

Disabling or uninstalling alone does not reset the policy in the running process. Restarting ends that process and clears the override. With the extension disabled or absent, it will not apply the override on the next launch. This is the designed restoration procedure; an end-to-end removal test has not yet been recorded for the original device.

Your Jami account is unrelated to the extension and should be kept intact. Do not use **Clear data** as an uninstall step.

## Troubleshooting

### I cannot find Extensions

Check official Jami's Advanced settings and record its exact version from About. Some builds or future versions may present extension support differently. This project has verified the version listed above, not every distribution. See Jami's [Android extension instructions](https://docs.jami.net/en_US/setup/jami-extensions-for-android.html).

### Jami says the certificate is untrusted

The supplied package is self-signed, not Jami Store certified. On the tested release, **Force install** was the supported way to approve it. If no such action appears, report the version and exact message. A self-signature does not mean Jami reviewed or endorsed the extension.

### Installation fails or the extension will not enable

Check that you downloaded the actual current `.jpl` file and did not extract/repack it. It contains an ARM64 library; other architectures are unsupported. Import it into official Jami, not a different app. If the file matches the published checksum but still fails, report the error, phone, Android version and Jami version.

### My microphone is still silent

Confirm the extension is enabled, then force stop and reopen official Jami with calls ended. Retest without Bluetooth. Check microphone mute, app permission and Android's microphone-access switch. Test a normal voice recording to establish whether the problem is Jami-specific. This workaround does not fix every cause of silence.

If a different calling/test app is installed, end its calls and stop it before retesting. The original investigation found a separate test app could leave stale call state behind.

### Jami says a call is in progress, but I cannot see one

Check for actual ongoing calls in all calling apps. End them before stopping any app. If an old test app is stuck, force stop that app and reopen official Jami. If the phone still has stale call state, an idle phone restart is a reasonable next check. Do not clear Jami's data or delete the account.

### I disabled it, but nothing changed

The process-level override persists until Jami exits. Force stop and reopen Jami after disabling or uninstalling it. Confirm it has not been re-enabled before retesting.

### A Jami or Android update broke it

This relies on extension loading and AAudio functions available on the tested system. Disable the extension, restart Jami, and report the versions and observed result. Compatibility with later versions is not guaranteed.

## Report a problem

Use the repository's [Issues](https://github.com/daniel-peter-dev/mmap-disabler/issues). Include phone model, Android/Jami/extension versions, exact error text and the steps tried. Mention whether Bluetooth and ordinary recordings work, and whether you fully restarted Jami.

Do not include passwords, recovery phrases, account exports, contact lists, voice recordings or full device logs. Developers can use the optional narrow log filter in the README; normal installation does not require it.
