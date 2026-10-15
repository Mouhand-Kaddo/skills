# Android operations

## Target and artifact

Set `PHONE_SERIAL` from fresh preflight. Use the same project-local ADB binary
throughout; running another SDK's ADB may disturb the shared server. Inspect
`adb devices -l` when choosing among transports. Do not restart the server,
enable network debugging or change host configuration as a routine retry.

For host-built APKs, resolve the project's SDK tools and inspect without keys:

```sh
sha256sum "$TEST_APK"
"$APK_ANALYZER" manifest application-id "$TEST_APK"
"$APK_ANALYZER" manifest version-code "$TEST_APK"
"$APK_SIGNER" verify --verbose --print-certs "$TEST_APK"
"$ADB" -s "$PHONE_SERIAL" shell dumpsys package "$TEST_PACKAGE"
```

Check these against the expected package, baseline signer and version before
installing. For a verified host-built APK, an authorized `adb -s SERIAL install
-r APK` replaces it while retaining data. Test-only flags are separate choices.
Inspect split-APK runners as a unit; one base APK hash does not identify all
installed splits. Use a project verifier or installed-APK hash/signer comparison
to establish installed identity; a matching version string alone is insufficient.
For artifacts required to stay on phone, use that project's on-phone verifier
and installation route instead of pulling them to the laptop.

If a framework command uninstalls its test app before/after running, allow it
only for an authorized disposable package; it cannot prove in-place retention.
Record `debug install` separately from observed Android installer confirmation.
When installer consent or permission UX is the subject of a test, exercise the
actual UI; an ADB bypass supplies no evidence for that flow.

## UI and narrowly scoped evidence

Use current UI hierarchy text/resource IDs/bounds, or inspect a fresh screenshot
when the framework exposes no useful hierarchy. If coordinate input is needed,
derive it from that capture and verify the resulting screen before continuing.
Wait for an observable state with a deadline rather than accumulating sleeps.
On a locked phone or a personal screen, request the necessary user action;
collect captures only once the approved test screen is visible.

Useful primitives (resolve variables; choose only those the case needs):

```sh
"$ADB" -s "$PHONE_SERIAL" shell am start -n "$TEST_COMPONENT"
"$ADB" -s "$PHONE_SERIAL" exec-out screencap -p > "$RUN_DIR/screen.png"
"$ADB" -s "$PHONE_SERIAL" shell input keyevent KEYCODE_HOME
"$ADB" -s "$PHONE_SERIAL" shell dumpsys activity activities
```

Inspect screenshots with the available image viewer. For hierarchy dumps, use
a unique temporary path, parse only the relevant test controls, and clean up
only that file when authorized. Avoid whole-phone bugreports, private data
directories, credential views and full logcat exports. Use a bounded time/PID
window and known safe test markers; refresh the PID after process restart.
Public signing certificate digests are enough; never inspect private keys.

Instrumentation can fail while ADB exits successfully. Require the runner's
documented completion status **and** the named assertion/test results; reject
failure/crash markers. An expected crash needs the matching follow-up recovery
assertion. Flutter success must include the suite result, not just installation
or the first passing case. Preserve pipeline exit codes when teeing output.

## Local backend and clock

Prove the fixture is loopback-only and uses an isolated database before starting
the app. Record existing `adb -s SERIAL reverse --list` mappings. Add only the
required port with `reverse --no-rebind tcp:PORT tcp:PORT`; preserve a mapping
already serving the intended fixture, and stop on an unrelated conflict.
Afterward remove only a mapping this run created, not all mappings.

Compare phone time (`adb -s SERIAL shell date -u`) with server time and fixture
clock mode. Synthetic event time and real JWT expiry may deliberately differ;
record both. Restore the real fixture clock for real GPS. Correct stale setup
and rerun rather than rewriting the recorded sensor timestamps. Use only new
test identities; report renewal status codes and queue counts without tokens.

## Background and other lifecycle cases

1. Establish the baseline queue/backend cursor and the phase-start timestamp.
2. Background the app using Home and independently observe which activity is
   resumed. Observe the launcher or another approved foreground app during the
   test; record sampling gaps. Check it is still foreground at the outcome.
3. Correlate a **new** event captured after the phase began with its queue record
   and server receipt, using an ID or exact timestamp in the isolated fixture.
   An arbitrary upload 200 may belong to an earlier event.
4. Resume the app only after the outcome or deadline is recorded. Verify queue
   and persisted effects, including duplicates and retained original timestamps.

For a physical-sensor claim, use unmocked fixes and the normal upload threshold.
Record if the harness requested a fix: that can prove background capture/upload,
but does not prove indefinite autonomous sampling. Native queue injection proves
transport/retry, not physical collection. A moved synthetic fence can prove
transitions with real GPS without proving real travel between locations.

Define separate cases for screen-off, process death, explicit force-stop, Doze,
reboot and offline behavior. Use only already authorized lifecycle actions and
record the actual mechanism. Home does not kill the app; force-stop is not a
surrogate for every OS kill. A USB reverse mapping depends on the laptop and
cannot establish detached operation. Phone-wide settings require the applicable
authorization and an explicit restoration check.

## Command references

Prefer the installed tools' help for supported flags. Official references:
[ADB](https://developer.android.com/tools/adb),
[ADB command manual](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/docs/user/adb.1.md),
[APK signature verification](https://developer.android.com/tools/apksigner).
