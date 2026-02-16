#!/usr/bin/env python3
import argparse
import getpass
import os
import re
import subprocess
import sys

from config import DEFAULTS, SETUP_DIR, logger


def run_script(script_name: str, env: dict | None = None, stdin: str | None = None):
    """Run a setup script with optional env vars and stdin."""
    script_path = SETUP_DIR / script_name
    result = subprocess.run(
        ["bash", str(script_path)],
        env=env,
        input=stdin,
        text=True,
        capture_output=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")


def prompt(message: str, default: str | None = None) -> str:
    """Prompt for input with optional default."""
    if default:
        response = input(f"{message} [{default}]: ").strip()
        return response if response else default
    return input(f"{message}: ").strip()


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """Prompt for yes/no."""
    hint = "Y/n" if default else "y/N"
    response = input(f"{message} [{hint}]: ").strip().lower()
    if not response:
        return default
    return response in ("y", "yes")


def list_wireless_interfaces() -> list[str]:
    """Return wireless interface names discovered on the host."""
    interfaces: list[str] = []

    try:
        result = subprocess.run(
            ["iw", "dev"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                match = re.match(r"\s*Interface\s+(\S+)", line)
                if match:
                    interfaces.append(match.group(1))
    except FileNotFoundError:
        pass

    if interfaces:
        return sorted(set(interfaces))

    try:
        result = subprocess.run(
            ["ip", "-o", "link", "show"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                match = re.match(r"\d+:\s*([^:]+):", line)
                if match:
                    iface = match.group(1).split("@", 1)[0]
                    if iface.startswith("wlan"):
                        interfaces.append(iface)
    except FileNotFoundError:
        pass

    return sorted(set(interfaces))


def interface_exists(interface: str) -> bool:
    """Check whether a network interface exists."""
    try:
        result = subprocess.run(
            ["ip", "link", "show", interface],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def choose_default_ap_interface(config_default: str) -> str:
    """Prefer a detected wireless interface over the static default."""
    detected = list_wireless_interfaces()
    if not detected:
        return config_default

    if config_default in detected:
        return config_default

    return detected[0]


def configure_hostapd(interface: str, ssid: str, country: str, passphrase: str):
    """Run 02-configure-hostapd.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = interface
    env["AP_SSID"] = ssid
    env["AP_COUNTRY"] = country
    run_script("02-configure-hostapd.sh", env=env, stdin=passphrase + "\n")


def configure_dnsmasq(interface: str, gateway: str):
    """Run 03-configure-dnsmasq.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = interface
    env["AP_GATEWAY"] = gateway
    run_script("03-configure-dnsmasq.sh", env=env)


def configure_network_manager(interface: str):
    """Run 04-configure-network-manager.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = interface
    run_script("04-configure-network-manager.sh", env=env)


def setup_nat(ap_interface: str, wan_interface: str):
    """Run 05-setup-nat.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = ap_interface
    env["WAN_INTERFACE"] = wan_interface
    run_script("05-setup-nat.sh", env=env)


def setup_service(interface: str, gateway: str):
    """Run 06-setup-service.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = interface
    env["AP_GATEWAY"] = gateway
    run_script("06-setup-service.sh", env=env)


def enable_services(interface: str):
    """Run 07-enable-services.sh"""
    env = os.environ.copy()
    env["AP_INTERFACE"] = interface
    run_script("07-enable-services.sh", env=env)


def configure_mdns():
    """Run 08-configure-mdns.sh"""
    run_script("08-configure-mdns.sh")


def read_passphrase_from_stdin() -> str:
    passphrase = sys.stdin.readline().strip()
    if not passphrase:
        logger.error("Error: passphrase required via stdin")
        sys.exit(1)
    return passphrase


def main():
    parser = argparse.ArgumentParser(description="Pi Bridge Setup")
    parser.add_argument(
        "--use-defaults",
        action="store_true",
        help="Use all defaults, read passphrase from stdin",
    )
    args = parser.parse_args()

    logger.info("=== Pi Bridge Setup ===")

    if args.use_defaults:
        interface = choose_default_ap_interface(DEFAULTS["DEFAULT_AP_INTERFACE"])
        ssid = DEFAULTS["DEFAULT_AP_SSID"]
        country = DEFAULTS["DEFAULT_AP_COUNTRY"]
        gateway = DEFAULTS["DEFAULT_AP_GATEWAY"]
        wan_interface = DEFAULTS["DEFAULT_WAN_INTERFACE"]
        enable_mdns = False
        passphrase = read_passphrase_from_stdin()
    else:
        logger.info("(Press Enter to accept defaults shown in brackets)\n")
        default_interface = choose_default_ap_interface(DEFAULTS["DEFAULT_AP_INTERFACE"])
        interface = prompt("AP interface", default=default_interface)
        ssid = prompt("Network SSID", default=DEFAULTS["DEFAULT_AP_SSID"])

        if DEFAULTS["DEFAULT_AP_COUNTRY"] == "US":
            if prompt_yes_no("Are you in the United States?", default=True):
                country = "US"
            else:
                country = prompt("Country code (e.g., GB, DE, CA)").upper()
        else:
            country = prompt("Country code", default=DEFAULTS["DEFAULT_AP_COUNTRY"]).upper()

        passphrase = getpass.getpass("AP passphrase: ")
        gateway = prompt("AP gateway IP", default=DEFAULTS["DEFAULT_AP_GATEWAY"])
        wan_interface = prompt("WAN interface (internet uplink)", default=DEFAULTS["DEFAULT_WAN_INTERFACE"])
        enable_mdns = prompt_yes_no("Enable mDNS reflection (device discovery across networks)?", default=False)

    logger.info(f"\nAP interface: {interface}")
    logger.info(f"WAN interface: {wan_interface}")
    logger.info(f"SSID:         {ssid}")
    logger.info(f"Country:      {country}")
    logger.info(f"Gateway:      {gateway}")
    logger.info(f"mDNS:         {'enabled' if enable_mdns else 'disabled'}")
    logger.info("")

    if not interface_exists(interface):
        available = list_wireless_interfaces()
        if available:
            logger.error(
                f"AP interface '{interface}' not found. Available wireless interfaces: "
                + ", ".join(available)
            )
        else:
            logger.error(
                f"AP interface '{interface}' not found. No wireless interfaces were detected."
            )
        sys.exit(1)

    if not args.use_defaults and not prompt_yes_no("Proceed with setup?", default=True):
        logger.info("Aborted.")
        return

    logger.info("")
    configure_hostapd(interface, ssid, country, passphrase)
    configure_dnsmasq(interface, gateway)
    configure_network_manager(interface)
    setup_nat(interface, wan_interface)
    setup_service(interface, gateway)
    enable_services(interface)
    if enable_mdns:
        configure_mdns()

    logger.info("\n=== Setup complete ===")


if __name__ == "__main__":
    main()
