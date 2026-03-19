"""Visual QA Automation — Main Entry Point.

Drives the Flutter dating app through use cases on an Android emulator
via ADB + uiautomator. Captures screenshots, detects screens, navigates
by text, and generates pass/fail reports.

Usage:
    python run_visual_qa.py --use-case onboarding
    python run_visual_qa.py --use-case all
    python run_visual_qa.py --use-case all --update-baselines
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure the visual-qa directory is on the path
sys.path.insert(0, str(Path(__file__).parent))

from adb_client import AdbClient
from navigator import Navigator
from report import generate_json_report, generate_markdown_report
from use_cases.onboarding import ONBOARDING_FLOW, ONBOARDING_TERMINAL_SCREENS
from use_cases.discovery import DISCOVERY_FLOW, DISCOVERY_TERMINAL_SCREENS
from use_cases.messaging import MESSAGING_FLOW, MESSAGING_TERMINAL_SCREENS
from use_cases.safety import SAFETY_FLOW, SAFETY_TERMINAL_SCREENS


USE_CASES = {
    "onboarding": ("UC1: Onboarding", ONBOARDING_FLOW, ONBOARDING_TERMINAL_SCREENS),
    "discovery": ("UC2: Discovery", DISCOVERY_FLOW, DISCOVERY_TERMINAL_SCREENS),
    "messaging": ("UC3: Messaging", MESSAGING_FLOW, MESSAGING_TERMINAL_SCREENS),
    "safety": ("UC4: Safety & Privacy", SAFETY_FLOW, SAFETY_TERMINAL_SCREENS),
}


def main():
    parser = argparse.ArgumentParser(description="Visual QA Automation for DatingApp")
    parser.add_argument(
        "--use-case",
        choices=["onboarding", "discovery", "messaging", "safety", "all"],
        default="all",
        help="Which use case to run (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        default="/app/test-results",
        help="Directory for test results (default: /app/test-results)",
    )
    parser.add_argument(
        "--adb-host",
        default=None,
        help="ADB host (default: from ADB_HOST env or localhost)",
    )
    parser.add_argument(
        "--adb-port",
        default=None,
        help="ADB port (default: from ADB_PORT env or 5555)",
    )
    parser.add_argument(
        "--apk-path",
        default=None,
        help="Path to APK to install (default: from APK_PATH env)",
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip emulator setup (assume app is already running)",
    )
    parser.add_argument(
        "--settle-time",
        type=float,
        default=2.0,
        help="Seconds to wait between actions (default: 2.0)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize ADB client
    adb = AdbClient(host=args.adb_host, port=args.adb_port)
    print(f"🔌 Connecting to emulator at {adb.serial}...")

    if not args.skip_setup:
        if not adb.connect():
            print("❌ Failed to connect to emulator")
            sys.exit(1)
        print("✅ Connected to emulator")

        print("⏳ Waiting for emulator boot...")
        if not adb.wait_for_boot():
            print("❌ Emulator did not boot in time")
            sys.exit(1)
        print("✅ Emulator booted")

        # Install APK if provided
        apk_path = args.apk_path or __import__("os").environ.get("APK_PATH")
        if apk_path and Path(apk_path).exists():
            print(f"📦 Installing APK: {apk_path}")
            if adb.install_apk(apk_path):
                print("✅ APK installed")
            else:
                print("⚠️  APK install failed — continuing anyway")

        # Grant permissions and launch
        adb.grant_permissions()
        adb.launch_app()
        print("🚀 App launched, waiting for render...")
        time.sleep(5)

    # Determine which use cases to run
    if args.use_case == "all":
        cases_to_run = list(USE_CASES.keys())
    else:
        cases_to_run = [args.use_case]

    # Run use cases
    nav = Navigator(adb, output_dir=output_dir, settle_time=args.settle_time)
    results = []

    for case_key in cases_to_run:
        name, flow, terminal = USE_CASES[case_key]
        print(f"\n{'='*60}")
        print(f"▶ Running: {name}")
        print(f"{'='*60}")

        result = nav.run_flow(name, flow, terminal)
        results.append(result)

        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"\n{status}: {name} ({len(result.steps)} steps, {result.duration_ms}ms)")
        if result.error:
            print(f"  Error: {result.error}")

        # Reset app between use cases (unless last one)
        if case_key != cases_to_run[-1]:
            print("\n🔄 Resetting app for next use case...")
            adb.clear_app()
            time.sleep(2)
            adb.launch_app()
            time.sleep(5)

    # Generate reports
    print(f"\n{'='*60}")
    print("📊 Generating reports...")
    json_path = generate_json_report(results, output_dir / "visual-qa-report.json")
    md_path = generate_markdown_report(results, output_dir / "visual-qa-report.md")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")

    # Summary
    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total_steps = sum(len(r.steps) for r in results)
    print(f"\n{'='*60}")
    print(f"📋 FINAL: {passed} passed, {failed} failed, {total_steps} total steps")
    print(f"{'='*60}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
