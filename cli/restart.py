#!/usr/bin/env python3
import subprocess
import sys

from config import logger, DEFAULTS


def restart_service(service: str) -> bool:
    """Restart a service. Returns True if successful."""
    logger.info(f"  Restarting {service}...")
    result = subprocess.run(
        ["sudo", "systemctl", "restart", service],
        capture_output=True, text=True
    )
    return result.returncode == 0


def main():
    logger.info("=== Restarting AP Services ===\n")

    interface = DEFAULTS.get("DEFAULT_AP_INTERFACE", "wlan1")

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

    logger.info("")
    if failed:
        logger.error(f"Failed to restart: {', '.join(failed)}")
        sys.exit(1)
    else:
        logger.info("All services restarted successfully.")


if __name__ == "__main__":
    main()
