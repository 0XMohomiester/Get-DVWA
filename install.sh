#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "[+] This script must be run as root" 
    exit 1
fi
sudo apt install -y python3-pip
sudo apt install -y python3-pymysql
sudo apt install -y python3-pyfiglet
sudo apt install -y python3-termcolor
sudo python3 Get-DVWA.py
