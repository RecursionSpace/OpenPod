#!/bin/bash

# Installer for OpenPod, for more information see https://github.com/blokbot-io/OpenBlok/blob/master/install.sh

# ---------------------------------------------------------------------------- #
#                                     Help                                     #
# ---------------------------------------------------------------------------- #
Help()
{
    # Display Help
    echo "OpenPod instalation script"
    echo
    echo "h     Display this help"
    echo "u     Set custom URL for OpenPod"
    echo "d     Enable debug mode"
}


# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
URL="recursion.space"
DEBUG=0


# ---------------------------------------------------------------------------- #
#                                    Options                                   #
# ---------------------------------------------------------------------------- #
while getopts ":hud" flags; do
  case "${flags}" in
    h) # display Help
         Help
         exit;;
    u) # Custom URL endpoint
         URL="${OPTARG}";;
    d) DEBUG=1 ;;
    \?) echo "Invalid option: -${OPTARG}" >&2;
    exit 1 ;;
  esac
done

# -------------------------------- Verify Root ------------------------------- #
if [ "$EUID" -ne 0 ]
  then echo "Please run as root with sudo."
  exit
fi

# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #

# ---------------------------- Update System Time ---------------------------- #
sudo timedatectl set-timezone UTC
sudo apt-get install chrony -y
sudo chronyd -q

# ----------------------------------- unzip ---------------------------------- #
REQUIRED_PKG="unzip"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install unzip -y
else
    echo "unzip already installed, skipping..."
fi

# ------------------------------------ jq ------------------------------------ #
REQUIRED_PKG="jq"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install jq -y
else
    echo "jq already installed, skipping..."
fi

# -------------------------------- Python 3.11 ------------------------------- #
pytohn_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$pytohn_version" != "3.11" ]; then
    sudo apt install software-properties-common -y
    yes '' | sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get install python3.1 -y
else
    echo "Python 3.11 already installed"
fi

# ------------------------------- Clone OpenPod ------------------------------ #
set -e # Exit when any command fails.
sudo mkdir -p /opt
cd /opt
sudo git clone --single-branch --branch release https://github.com/RecursionSpace/OpenPod.git

# ----------------------------- Setup Enviroment ----------------------------- #
sudo apt-get install python3.11-venv -y
sudo python3.11 -m venv /opt/OpenPod/env
source /opt/OpenPod/env/bin/activate
sudo pip install --no-input -U -r /opt/OpenPod/requirements.txt --no-cache-dir --no-dependencies

# ---------------------------- Create Directories ---------------------------- #
sudo mkdir -p /opt/OpenPod/logs
sudo mkdir -p /opt/OpenPod/data

# ------------------------------- Create Files ------------------------------- #
sudo touch /opt/OpenPod/logs/RecursionLog.log
sudo touch /opt/OpenPod/logs/System.Snapshot
sudo touch /opt/OpenPod/data/dump.json
sudo touch /opt/OpenPod/data/nodes.json
sudo touch /opt/OpenPod/data/owners.json
sudo touch /opt/OpenPod/data/permissions.json

# -------------------------------- system.json ------------------------------- #
sudo touch /opt/OpenPod/system.json
serial_uuid=$(cat /proc/sys/kernel/random/uuid)
xbee_uuid=$(cat /proc/sys/kernel/random/uuid)
echo '{
    "serial": '"'$serial_uuid'"',
    "timezone": "UTC",
    "XBEE_KY": '"'$xbee_uuid'"',
    "XBEE_OP": "0",
    "url": '"'$URL'"',
    "version": "0_0_1",
    "debug": '"'$DEBUG'"'
}' > /opt/OpenPod/system.json

# --------------------------- Setup OpenPod Service -------------------------- #
cat <<EOF > /etc/systemd/system/openpod.service
[Unit]
Description=OpenPod
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/OpenPod
ExecStart=/opt/OpenPod/env/bin/python3.11 /opt/OpenPod/OpenPod.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now openpod.service
sudo systemctl daemon-reload

echo "OpenPod is now installed"
exit 0
