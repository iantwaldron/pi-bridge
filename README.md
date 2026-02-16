# Pi Bridge
[![Tests](https://github.com/iantwaldron/pi-bridge/actions/workflows/pytest.yml/badge.svg)](https://github.com/iantwaldron/pi-bridge/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/iantwaldron/pi-bridge/graph/badge.svg?token=VMFH7R4D8B)](https://codecov.io/gh/iantwaldron/pi-bridge)

`pi-bridge` turns a Raspberry Pi into a Wi-Fi access point and network bridge.
It configures `hostapd`, `dnsmasq`, static interface IP, NAT forwarding rules, and related system services, then gives you a small CLI to manage and inspect the AP.

## Requirements

- Raspberry Pi OS / Debian-based Linux with systemd
- `sudo` access
- A wireless interface for the AP (default: `wlan1`)
- An uplink/WAN interface with internet access (default: `eth0`)

## Install

```bash
git clone https://github.com/iantwaldron/pi-bridge.git ~/pi-bridge
cd ~/pi-bridge
source first-setup.sh
```

This adds `bin/pi-bridge` to your shell `PATH`.

## Setup

1. Install dependencies/firmware:

```bash
pi-bridge install-deps
```

2. Reboot the Pi.

3. Run AP setup:

Interactive setup:

```bash
pi-bridge setup
```

Non-interactive setup with defaults:

```bash
echo "your-passphrase" | pi-bridge setup --use-defaults
```

Defaults are defined in `setup/defaults.sh`.

## Common Commands

```bash
pi-bridge status
pi-bridge start
pi-bridge stop
pi-bridge restart
pi-bridge clients
pi-bridge logs
pi-bridge install-deps
pi-bridge forwarding list
pi-bridge interface show
pi-bridge interface switch wlan1 --wan eth0
```

## Notes

- Setup writes to system config under `/etc`, modifies `iptables`, and manages system services.
- Run this on a real Pi host you intend to configure (not your primary workstation).
