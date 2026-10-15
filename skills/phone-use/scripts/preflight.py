#!/usr/bin/env python3
"""Read ADB identity only. Exit 0 means ready for inspection, never a test pass."""

import argparse
from datetime import datetime, timezone
import json
import subprocess


PROPERTIES = (
    "ro.product.manufacturer", "ro.product.model", "ro.build.version.release",
    "ro.build.version.sdk", "ro.product.cpu.abi", "ro.hardware",
    "ro.kernel.qemu", "ro.boot.qemu", "sys.boot_completed",
)
VIRTUAL_MARKERS = ("ranchu", "goldfish", "cuttlefish", "vsoc", "sdk_gphone", "emulator")


class PreflightError(RuntimeError):
    """A device cannot currently be selected safely for physical testing."""


def run_command(command):
    try:
        return subprocess.run(
            command, capture_output=True, text=True, check=True, timeout=4
        ).stdout
    except FileNotFoundError as error:
        raise PreflightError("ADB missing; use the project's SDK path with --adb.") from error
    except subprocess.TimeoutExpired as error:
        raise PreflightError("ADB timed out; check the connection without restarting shared services.") from error
    except (subprocess.CalledProcessError, OSError) as error:
        raise PreflightError("ADB command failed; check its path, permissions and connection.") from error


def inspect_device(adb, serial=None, runner=run_command):
    inventory = runner([adb, "devices", "-l"])
    if "List of devices attached" not in inventory:
        raise PreflightError("Unrecognized ADB inventory; select no device.")
    rows = inventory.split("List of devices attached", 1)[1].splitlines()
    devices = [row.split() for row in rows if row.strip()]
    if not devices:
        raise PreflightError("No device connected. Physical checks remain blocked.")
    if serial is None:
        if len(devices) != 1:
            raise PreflightError("Multiple devices listed; select the intended phone with --serial.")
        serial = devices[0][0]
    selected = [row for row in devices if row[0] == serial]
    if len(selected) != 1:
        raise PreflightError("Requested serial is not connected; do not switch targets.")
    row = selected[0]
    if len(row) < 2 or row[1] != "device":
        state = " ".join(row[1:3])
        raise PreflightError(f"Selected device is not ready ({state}); check USB authorization/connection.")
    if serial.startswith("emulator-"):
        raise PreflightError("Selected target is virtual; it cannot establish physical-phone evidence.")

    def query(*args):
        return runner([adb, "-s", serial, *args]).strip()

    if query("get-state") != "device":
        raise PreflightError("Selected device disconnected during preflight.")
    identity = {name: query("shell", "getprop", name) for name in PROPERTIES}
    description = " ".join(identity[name].lower() for name in
                           ("ro.product.model", "ro.hardware", "ro.product.manufacturer"))
    if any(identity[name] not in ("", "0") for name in ("ro.kernel.qemu", "ro.boot.qemu")) or any(
        marker in description for marker in VIRTUAL_MARKERS
    ):
        raise PreflightError("Selected target reports virtual hardware; physical checks remain blocked.")
    if any(not identity[name] for name in PROPERTIES[:6]) or not identity["ro.build.version.sdk"].isdigit():
        raise PreflightError("Device identity is incomplete; verify the target before testing.")
    if identity["sys.boot_completed"] != "1":
        raise PreflightError("Device has not finished booting; recheck when ready.")
    return {
        "status": "ready", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "serial": serial, "identity": identity, "application_tested": False,
        "limitation": "ADB properties are identity hints, not hardware attestation. Match the intended phone.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default="adb", help="Project-local ADB executable")
    parser.add_argument("--serial", help="Required when multiple transports are listed")
    args = parser.parse_args()
    try:
        report = inspect_device(args.adb, args.serial)
    except PreflightError as error:
        print(json.dumps({"status": "blocked", "reason": str(error), "application_tested": False}))
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
