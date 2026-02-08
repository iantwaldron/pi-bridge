#!/usr/bin/env python3
import subprocess
import sys

from config import logger, DEFAULTS


def control_service(service: str, action: str) -> bool:
    """Start or stop a service. Returns True if successful."""
    logger.info(f"  {action.capitalize()}ing {service}...")
    result = subprocess.run(
        ["sudo", "systemctl", action, service],
        capture_output=True, text=True
    )
    return result.returncode == 0


def stop_ap():
    """Stop all AP services."""
    logger.info("=== Stopping AP ===\n")

    interface = DEFAULTS.get("DEFAULT_AP_INTERFACE", "wlan1")

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

    logger.info("")
    if failed:
        logger.error(f"Failed to stop: {', '.join(failed)}")
        sys.exit(1)
    else:
        logger.info("AP stopped.")


def start_ap():
    """Start all AP services."""
    logger.info("=== Starting AP ===\n")

    interface = DEFAULTS.get("DEFAULT_AP_INTERFACE", "wlan1")

    services = [
        f"{interface}-static-ip",
        "hostapd",
        "dnsmasq",
    ]

    failed = []
    for service in services:
        if not control_service(service, "start"):
            failed.append(service)

    logger.info("")
    if failed:
        logger.error(f"Failed to start: {', '.join(failed)}")
        sys.exit(1)
    else:
        logger.info("AP started.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop"])
    args = parser.parse_args()

    if args.action == "stop":
        stop_ap()
    else:
        start_ap()
