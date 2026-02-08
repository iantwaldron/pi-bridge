#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path

from config import logger, DEFAULTS


def get_wireless_clients(interface: str) -> list[dict]:
    """Get list of connected wireless clients."""
    result = subprocess.run(
        ["iw", "dev", interface, "station", "dump"],
        capture_output=True, text=True
    )

    clients = []
    if result.returncode == 0:
        current_mac = None
        for line in result.stdout.splitlines():
            if line.startswith("Station "):
                current_mac = line.split()[1]
                clients.append({"mac": current_mac})
            elif current_mac and "signal:" in line:
                match = re.search(r'signal:\s+(-?\d+)', line)
                if match:
                    clients[-1]["signal"] = f"{match.group(1)} dBm"

    return clients


def get_dhcp_leases() -> dict[str, dict]:
    """Get DHCP leases from dnsmasq. Returns dict keyed by MAC."""
    leases = {}
    lease_file = Path("/var/lib/misc/dnsmasq.leases")

    try:
        if lease_file.exists():
            for line in lease_file.read_text().splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    # Format: timestamp mac ip hostname client-id
                    mac = parts[1].lower()
                    leases[mac] = {
                        "ip": parts[2],
                        "hostname": parts[3] if parts[3] != "*" else ""
                    }
    except PermissionError:
        result = subprocess.run(
            ["sudo", "cat", str(lease_file)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    mac = parts[1].lower()
                    leases[mac] = {
                        "ip": parts[2],
                        "hostname": parts[3] if parts[3] != "*" else ""
                    }

    return leases


def main():
    logger.info("=== Connected Clients ===\n")

    interface = DEFAULTS.get("DEFAULT_AP_INTERFACE", "wlan1")

    clients = get_wireless_clients(interface)
    leases = get_dhcp_leases()

    if not clients:
        logger.info("No clients connected.")
        return

    # Merge wireless info with DHCP info
    for client in clients:
        mac = client["mac"].lower()
        if mac in leases:
            client["ip"] = leases[mac]["ip"]
            client["hostname"] = leases[mac]["hostname"]

    # Print table
    logger.info(f"{'MAC Address':<20} {'IP Address':<16} {'Signal':<12} {'Hostname'}")
    logger.info("-" * 70)
    for client in clients:
        mac = client.get("mac", "")
        ip = client.get("ip", "-")
        signal = client.get("signal", "-")
        hostname = client.get("hostname", "-") or "-"
        logger.info(f"{mac:<20} {ip:<16} {signal:<12} {hostname}")

    logger.info(f"\nTotal: {len(clients)} client(s)")


if __name__ == "__main__":
    main()
