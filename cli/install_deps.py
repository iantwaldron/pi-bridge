#!/usr/bin/env python3
import argparse
import os
import subprocess

from config import DEFAULTS, SETUP_DIR, logger


def run_script(script_name: str, env: dict | None = None):
    script_path = SETUP_DIR / script_name
    result = subprocess.run(
        ["bash", str(script_path)],
        env=env,
        text=True,
        capture_output=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")


def prompt_choice(message: str, choices: list[str], default: str | None = None) -> str:
    choice_str = "/".join(choices)
    if default:
        response = input(f"{message} ({choice_str}) [{default}]: ").strip().lower()
        return response if response else default
    while True:
        response = input(f"{message} ({choice_str}): ").strip().lower()
        if response in choices:
            return response
        logger.warning(f"Please enter one of: {choice_str}")


def install_packages(chipset: str):
    env = os.environ.copy()
    env["WIFI_CHIPSET"] = chipset
    run_script("01-install-packages.sh", env=env)


def main():
    parser = argparse.ArgumentParser(description="Install Pi Bridge dependencies and firmware")
    parser.add_argument("--use-defaults", action="store_true", help="Use default chipset")
    parser.add_argument("--chipset", choices=["intel", "realtek"], help="WiFi chipset")
    args = parser.parse_args()

    logger.info("=== Pi Bridge Dependency Install ===")

    if args.chipset:
        chipset = args.chipset
    elif args.use_defaults:
        chipset = DEFAULTS["DEFAULT_WIFI_CHIPSET"]
    else:
        chipset = prompt_choice(
            "WiFi chipset",
            ["intel", "realtek"],
            default=DEFAULTS["DEFAULT_WIFI_CHIPSET"],
        )

    logger.info(f"\nChipset: {chipset}")
    logger.info("")

    install_packages(chipset)

    logger.info("\n=== Dependency install complete ===")
    logger.info("Reboot recommended before running `pi-bridge setup`.")


if __name__ == "__main__":
    main()
