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


def restart_service(service: str) -> bool:
    """Restart a service. Returns True if successful."""
    print(f"  Restarting {service}...")
    result = subprocess.run(
        ["sudo", "systemctl", "restart", service],
        capture_output=True, text=True
    )
    return result.returncode == 0


def main():
    print("=== Restarting AP Services ===\n")

    defaults = load_defaults()
    interface = defaults.get("DEFAULT_AP_INTERFACE", "wlan1")

    services = [
        "NetworkManager",
        f"{interface}-static-ip",
        "hostapd",
        "dnsmasq",
    ]

    failed = []
    for service in services:
        if not restart_service(service):
            failed.append(service)

    print()
    if failed:
        print(f"Failed to restart: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("All services restarted successfully.")


if __name__ == "__main__":
    main()
