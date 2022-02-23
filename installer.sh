#!/bin/bash

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


# ---------------------------------------------------------------------------- #
#                                   Installer                                  #
# ---------------------------------------------------------------------------- #

# ---------------------- Update Package List and Upgrade --------------------- #
sudo apt-get update -y && sudo apt-get upgrade -y

# ---------------------------- Update System Time ---------------------------- #
sudo timedatectl set-timezone UTC
sudo apt-get install chrony -y
sudo chronyd -q

# ------------------------- Install Bash Requirements ------------------------ #
sudo apt-get install jq -y
sudo apt-get install unzip -y

# ---------------------------- Install Python 3.10 --------------------------- #
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10 -y

# ------------------------------- Clone OpenPod ------------------------------ #
set -e # Exit when any command fails.
sudo mkdir -p /opt
sudo git clone  --single-branch --branch release https://github.com/RecursionSpace/OpenPod.git /opt/

# ----------------------------- Setup Enviroment ----------------------------- #
sudo apt-get install python3.10-venv -y
sudo python3.10 -m venv /opt/OpenPod/env
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
ExecStart=/opt/OpenPod/env/bin/python3.10 /opt/OpenPod/OpenPod.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now openpod.service
sudo systemctl daemon-reload

echo "OpenPod is now installed"
exit 0
