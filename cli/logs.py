#!/usr/bin/env python3
import subprocess
import sys
import argparse


def show_logs(service: str, follow: bool = False, lines: int = 50):
    """Show logs for a service using journalctl."""
    cmd = ["sudo", "journalctl", "-u", service, "-n", str(lines)]
    if follow:
        cmd.append("-f")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(description="View AP service logs")
    parser.add_argument("service", nargs="?", default="hostapd",
                        choices=["hostapd", "dnsmasq", "all"],
                        help="Service to view logs for (default: hostapd)")
    parser.add_argument("-f", "--follow", action="store_true",
                        help="Follow log output")
    parser.add_argument("-n", "--lines", type=int, default=50,
                        help="Number of lines to show (default: 50)")
    args = parser.parse_args()

    print(f"=== {args.service.title()} Logs ===\n")

    if args.service == "all":
        for svc in ["hostapd", "dnsmasq"]:
            print(f"--- {svc} ---")
            show_logs(svc, follow=False, lines=args.lines // 2)
            print()
    else:
        show_logs(args.service, follow=args.follow, lines=args.lines)


if __name__ == "__main__":
    main()
