#!/bin/bash
echo "Installing required packages..."
sudo apt update
sudo apt install -y firmware-iwlwifi hostapd dnsmasq iptables-persistent