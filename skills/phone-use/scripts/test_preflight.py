"""Simulated ADB boundary tests; these are not physical-device evidence."""

import subprocess
import unittest

from preflight import PreflightError, inspect_device, run_command


class AdbFixture:
    def __init__(self, inventory=None, properties=None):
        self.inventory = inventory if inventory is not None else (
            "List of devices attached\nTEST_PHONE device usb:1 model:SM_S918B\n"
        )
        self.properties = {
            "ro.product.manufacturer": "samsung",
            "ro.product.model": "SM-S918B",
            "ro.build.version.release": "16",
            "ro.build.version.sdk": "36",
            "ro.product.cpu.abi": "arm64-v8a",
            "ro.hardware": "qcom",
            "ro.kernel.qemu": "",
            "ro.boot.qemu": "",
            "sys.boot_completed": "1",
        }
        self.properties.update(properties or {})
        self.calls = []

    def __call__(self, command):
        self.calls.append(command)
        if command == ["adb-fixture", "devices", "-l"]:
            return self.inventory
        if command[1:3] != ["-s", "TEST_PHONE"]:
            raise AssertionError(f"Unpinned device command: {command}")
        if command[3:] == ["get-state"]:
            return "device\n"
        if command[3:5] == ["shell", "getprop"] and len(command) == 6:
            return self.properties[command[5]] + "\n"
        raise AssertionError(f"Unexpected command: {command}")


class PreflightTests(unittest.TestCase):
    def test_ready_is_identity_evidence_not_an_application_pass(self):
        adb = AdbFixture()
        result = inspect_device("adb-fixture", runner=adb)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["serial"], "TEST_PHONE")
        self.assertEqual(result["identity"]["ro.product.model"], "SM-S918B")
        self.assertFalse(result["application_tested"])
        self.assertTrue(result["observed_at_utc"].endswith("+00:00"))
        self.assertEqual(len(adb.calls), 11)

    def test_empty_inventory_blocks(self):
        with self.assertRaisesRegex(PreflightError, "No device"):
            inspect_device("adb-fixture", runner=AdbFixture("List of devices attached\n"))

    def test_invalid_inventory_blocks(self):
        with self.assertRaisesRegex(PreflightError, "inventory"):
            inspect_device("adb-fixture", runner=AdbFixture("unrecognized output"))

    def test_multiple_devices_require_selection(self):
        adb = AdbFixture("List of devices attached\nTEST_PHONE device\nemulator-5554 device\n")
        with self.assertRaisesRegex(PreflightError, "--serial"):
            inspect_device("adb-fixture", runner=adb)
        self.assertEqual(len(adb.calls), 1)
        self.assertEqual(inspect_device("adb-fixture", "TEST_PHONE", adb)["serial"], "TEST_PHONE")

    def test_explicit_missing_serial_does_not_fall_back(self):
        with self.assertRaisesRegex(PreflightError, "not connected"):
            inspect_device("adb-fixture", "OTHER_PHONE", AdbFixture())

    def test_nonready_states_block_before_shell(self):
        for state in ("unauthorized", "offline", "recovery", "no permissions"):
            with self.subTest(state=state):
                adb = AdbFixture(f"List of devices attached\nTEST_PHONE {state}\n")
                with self.assertRaises(PreflightError):
                    inspect_device("adb-fixture", runner=adb)
                self.assertEqual(len(adb.calls), 1)

    def test_emulator_serial_blocks_before_shell(self):
        adb = AdbFixture("List of devices attached\nemulator-5554 device\n")
        with self.assertRaisesRegex(PreflightError, "virtual"):
            inspect_device("adb-fixture", runner=adb)
        self.assertEqual(len(adb.calls), 1)

    def test_virtual_device_with_phone_like_serial_blocks(self):
        for properties in ({"ro.kernel.qemu": "1"}, {"ro.boot.qemu": "1"},
                           {"ro.hardware": "ranchu"}, {"ro.product.model": "sdk_gphone64_arm64"}):
            with self.subTest(properties=properties), self.assertRaisesRegex(PreflightError, "virtual"):
                inspect_device("adb-fixture", runner=AdbFixture(properties=properties))

    def test_incomplete_identity_and_unfinished_boot_block(self):
        for properties in ({"ro.product.model": ""}, {"ro.build.version.sdk": "unknown"},
                           {"ro.hardware": ""}, {"sys.boot_completed": ""}):
            with self.subTest(properties=properties), self.assertRaises(PreflightError):
                inspect_device("adb-fixture", runner=AdbFixture(properties=properties))

    def test_disconnect_during_probe_blocks(self):
        fixture = AdbFixture()

        def disconnect(command):
            if command[-1] == "get-state":
                return "offline"
            return fixture(command)

        with self.assertRaisesRegex(PreflightError, "disconnected"):
            inspect_device("adb-fixture", runner=disconnect)

    def test_command_failure_timeout_and_missing_binary_are_bounded(self):
        from unittest.mock import patch

        failures = (FileNotFoundError(), subprocess.TimeoutExpired(["adb"], 4),
                    subprocess.CalledProcessError(1, ["adb"]))
        for failure in failures:
            with self.subTest(failure=type(failure).__name__), patch(
                "preflight.subprocess.run", side_effect=failure
            ) as execute, self.assertRaises(PreflightError):
                run_command(["adb", "devices", "-l"])
            self.assertEqual(execute.call_args.kwargs["timeout"], 4)
            self.assertTrue(execute.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
