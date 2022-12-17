#!/bin/bash

# Installer for OpenPod, for more information see https://github.com/blokbot-io/OpenBlok/blob/master/install.sh


# ---------------------------------------------------------------------------- #
#                                Disable Prompts                               #
# ---------------------------------------------------------------------------- #
export DEBIAN_FRONTEND=noninteractive
sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf


# ---------------------------------------------------------------------------- #
#                                     Help                                     #
# ---------------------------------------------------------------------------- #
Help()
{
    # Display Help
    echo "OpenPod instalation script"
    echo
    echo "h     Display this help"
    echo "b     Set custom branch for OpenPod"
    echo "u     Set custom URL for OpenPod"
    echo "d     Enable debug mode"
}


# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
DEBUG=flase # -d


# ---------------------------------------------------------------------------- #
#                                    Options                                   #
# ---------------------------------------------------------------------------- #
while getopts ":hud" flags; do
  case "${flags}" in
    h) # display Help
         Help
         exit;;
    b) # Custom branch
        branch="${OPTARG}";;
    d) # Enable debug mode
        DEBUG=true ;;
    u) # Custom URL endpoint
         URL="${OPTARG}";;
    \?) echo "Invalid option: -${OPTARG}" >&2;
    exit 1 ;;
  esac
done

if [ $DEBUG ]; then
    branch='dev-release'
    URL='dev.recursion.space'
    API_URL='dev.api.recursion.space'
elif [ ! $DEBUG ]; then
    branch='release'
    URL='recursion.space'
    API_URL='api.recursion.space'
fi

echo "Installing OpenPod with the following options:"
echo "Debug: $DEBUG"
echo "Branch: $branch"
echo "URL: $URL"
echo "API_URL: $API_URL"

# -------------------------------- Verify Root ------------------------------- #
if [ "$EUID" -ne 0 ]
  then echo "Please run as root with sudo."
  exit
fi

# ---------------------------- Update System Time ---------------------------- #
sudo timedatectl set-timezone UTC


# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #

# ------------------------------ build-essential ----------------------------- #
# Required to install RPi.GPIO - https://github.com/ynsta/steamcontroller/issues/42
REQUIRED_PKG="build-essential"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install build-essential -y
else
    echo "build-essential already installed, skipping..."
fi

# ---------------------------------- chrony ---------------------------------- #
REQUIRED_PKG="chrony"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install chrony -y
    sudo chronyd -q
else
    echo "chrony already installed, skipping..."
fi

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
    sudo apt-get install python3.11 -y
else
    echo "Python 3.11 already installed"
fi

# -------------------------------- Python-Dev -------------------------------- #
REQUIRED_PKG="python3.11-dev"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install python3.11-dev -y
else
    echo "python3.11-dev already installed, skipping..."
fi

# ------------------------ Python Virtual Environment ------------------------ #
REQUIRED_PKG="python3.11-venv"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install python3.11-venv -y
else
    echo "python3.11-venv already installed, skipping..."
fi

# ---------------------------------------------------------------------------- #
#                                    OpenPod                                   #
# ---------------------------------------------------------------------------- #

# -------------------------- Clear Previous Install -------------------------- #
sudo rm -rf /opt/OpenPod

# ------------------------------- Clone OpenPod ------------------------------ #
set -e # Exit when any command fails.
sudo mkdir -p /opt
cd /opt
sudo git clone --single-branch --branch $branch https://github.com/RecursionSpace/OpenPod.git
cd OpenPod

# ----------------------------- Setup Enviroment ----------------------------- #
sudo python3.11 -m venv /opt/OpenPod/env
source /opt/OpenPod/env/bin/activate
pip install --no-input -U -r /opt/OpenPod/requirements.txt --no-cache-dir --no-dependencies

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
openpod_version=$(git rev-parse HEAD)
echo '{
    "debug": '$DEBUG',
    "serial": "'"$serial_uuid"'",
    "timezone": "UTC",
    "url": "'"$URL"'",
    "api_url": "'"$API_URL"'",
    "XBEE": {
        "KY": "'"$xbee_uuid"'",
        "OP": "0"
    },
    "GPIO": {
        "LED_IO": 23,
        "LED_STAT": 17
    },
    "version": "'"$openpod_version"'"
}' > /opt/OpenPod/system.json

# --------------------------- Setup OpenPod Service -------------------------- #
cat <<EOF > /etc/systemd/system/openpod.service
[Unit]
Description=OpenPod | Recursion.Space
After=network.target
StartLimitIntervalSec=0

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

echo "- OpenPod is now installed -"
exit 0
