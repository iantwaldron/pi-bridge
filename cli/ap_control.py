#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

SETUP_DIR = Path(__file__).parent.parent / "setup"


def load_defaults() -> dict[str, str]:
    """Parse defaults.sh and return as dict."""
    defaults = {}
    defaults_file = SETUP_DIR / "defaults.sh"
    for line in defaults_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            defaults[key] = value.strip('"')
    return defaults


def control_service(service: str, action: str) -> bool:
    """Start or stop a service. Returns True if successful."""
    print(f"  {action.capitalize()}ing {service}...")
    result = subprocess.run(
        ["sudo", "systemctl", action, service],
        capture_output=True, text=True
    )
    return result.returncode == 0


def stop_ap():
    """Stop all AP services."""
    print("=== Stopping AP ===\n")

    defaults = load_defaults()
    interface = defaults.get("DEFAULT_AP_INTERFACE", "wlan1")

    # Stop in reverse order
    services = [
        "dnsmasq",
        "hostapd",
        f"{interface}-static-ip",
    ]

    failed = []
    for service in services:
        if not control_service(service, "stop"):
            failed.append(service)

    print()
    if failed:
        print(f"Failed to stop: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("AP stopped.")


def start_ap():
    """Start all AP services."""
    print("=== Starting AP ===\n")

    defaults = load_defaults()
    interface = defaults.get("DEFAULT_AP_INTERFACE", "wlan1")

    services = [
        f"{interface}-static-ip",
        "hostapd",
        "dnsmasq",
    ]

    failed = []
    for service in services:
        if not control_service(service, "start"):
            failed.append(service)

    print()
    if failed:
        print(f"Failed to start: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("AP started.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop"])
    args = parser.parse_args()

    if args.action == "stop":
        stop_ap()
    else:
        start_ap()
