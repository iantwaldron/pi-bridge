#!/bin/bash
set -e

source "$(dirname "$0")/defaults.sh"

WIFI_CHIPSET="${WIFI_CHIPSET:-$DEFAULT_WIFI_CHIPSET}"

echo "Installing required packages..."
sudo apt update

if [ "$WIFI_CHIPSET" = "intel" ]; then
    echo "Installing Intel WiFi firmware..."
    sudo apt install -y firmware-iwlwifi
elif [ "$WIFI_CHIPSET" = "realtek" ]; then
    echo "Installing Realtek WiFi firmware..."
    sudo apt install -y firmware-realtek
else
    echo "Unknown chipset: $WIFI_CHIPSET" >&2
    exit 1
fi

echo "Installing networking packages..."
sudo apt install -y hostapd dnsmasq iptables-persistent

echo "Package installation complete."
