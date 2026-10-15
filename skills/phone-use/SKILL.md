---
name: phone-use
description: Phone testing on a real Android device. Use to run, test, reproduce a bug or verify a fix in an Android app on the connected physical phone over ADB.
---

# Phone use

Exercise the requested flow on the connected Android phone and leave **evidence** another agent can assess. Every claim rests on a fresh observation from this phone; the bundled preflight and commands are Android-only, so for another platform first identify its device tools.

This skill grants no new authority. Installation, credentials, production data, paid services and phone-wide settings stay within the user's existing authorization; ask only for a missing decision or a human-only action that blocks the next step.

## 1. Write the test contract

Read the repository's instructions, status and test entrypoint.

Write one **case** per flow: initial state → actions → observable expected result. Include the original failure sequence alongside the happy path. Tag each case's inputs (physical, synthetic, mixed) and its required observation (UI, stored state, backend effect, lifecycle). "Full E2E" means the named flows plus a list of remaining gaps.

Fix the permitted package, backend, install route, data that must survive, and any human-only step.

**Done when:** every case has an expected result and an evidence source, and the package, environment and permissions are explicit.

## 2. Confirm the phone

Run the read-only preflight from this skill's directory with the project's ADB:

```sh
python3 scripts/preflight.py --adb "$PROJECT_SDK/platform-tools/adb"
# Several transports listed: rerun with --serial "$PHONE_SERIAL".
```

Exit 2 means blocked; `ready` means connected, never passed. Compare model, Android version and ABI with the intended phone. Pass `-s "$PHONE_SERIAL"` to **every** later ADB command: screenshots, watchers, port mappings. Rerun preflight after any reconnect or device-changing event.

A missing, unauthorized or offline phone is a **blocked** branch: report the exact blocker, continue host-side work, and keep physical checks pending. Emulator results are separate evidence.

**Done when:** a fresh identity record matches the intended phone, or the physical branch is reported blocked.

## 3. Prepare the build and state

Read [Android operations](references/android.md) now; it covers installing, UI control, logs, backends and lifecycle cases. Inspect the chosen runner for resets, uninstalls, permission grants, test clocks and backend selection before running it.

Record the revision (with uncommitted changes), artifact hash, package, version and signer. Verify the artifact before the authorized install and the installed identity after it. Update tests keep the same package and signer with a non-default saved value; a signature conflict is a **blocker**.

A local backend uses disposable accounts and database, loopback, and a serial-scoped reverse mapping. Check phone and server UTC time before sensor tests. The app reads its own secrets; prompts, logs, screenshots and shell arguments stay credential-free.

**Done when:** the build, baseline and backend are identified, and preparation has substituted for no behavior under test.

## 4. Exercise and observe

Act through the phone UI or the project's real integration runner. Read the current hierarchy or screenshot before each control choice. A case passes on its visible result **and** its required persisted or backend effect, read from raw runner output against the expected assertions.

Label all test assistance: injected readings, explicit sync, permission pre-grants. Keep each lifecycle claim (background, screen-off, process death, force-stop, Doze, reboot, offline, detached laptop) its own case.

On failure: keep the failed attempt, capture narrow diagnostics, reproduce in the smallest test, fix within scope, then rerun the exact phone case on the rebuilt artifact plus neighboring cases. Change one setup cause per rerun. Assertions, timestamps and thresholds stay as written. Bound waits by the runner's timeout. A retry that needs new permission, absent hardware, or would overwrite unrelated state ends the case as blocked.

**Done when:** each case is pass, fail, blocked or not run, with actual versus expected; every fix has a fresh physical rerun or is marked pending.

## 5. Hand off

Restore only what this run **owns**: its temporary changes, mappings and helpers. Failures and app data stay. Verify restoration, or list what the user must restore.

Save a record in the project's validation location: timestamp, revision, device, artifact path and hash, install route, commands, raw result paths, and per case its inputs, assistance, expected and actual outcome, and evidence. Add coverage limits, pending checks, changed paths and the next task. Device IDs, coordinates and raw captures stay local unless sharing is authorized.

**Done when:** the record separates fresh physical evidence from host, emulator and historical results, and accounts for every case.
