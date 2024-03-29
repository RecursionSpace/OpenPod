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

# TO FIX: ARGS VS OPTS

# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
DEBUG=false # -d
REPO='https://github.com/RecursionSpace/OpenPod'

# ---------------------------------------------------------------------------- #
#                                    Options                                   #
# ---------------------------------------------------------------------------- #
while getopts ":hbdu" flags; do
  case "${flags}" in
    h) # display Help
         Help
         exit;;
    b) # Custom branch
        BRANCH="${OPTARG}";;
    d) # Enable debug mode
        DEBUG=true ;;
    u) # Custom URL endpoint
         URL="${OPTARG}";;
    \?) echo "Invalid option: -${OPTARG}" >&2;
    exit 1 ;;
  esac
done

if [ "$DEBUG" = true ]; then
    BRANCH='dev-release'
    URL='dev.recursion.space'
    API_URL='dev.api.recursion.space'
else
    BRANCH='release'
    URL='recursion.space'
    API_URL='api.recursion.space'
fi

echo "Installing OpenPod with the following options:"
echo "Debug   | $DEBUG"
echo "Repo    | $REPO"
echo "Branch  | $BRANCH"
echo "URL     | $URL"
echo "API_URL | $API_URL"

# -------------------------------- Verify Root ------------------------------- #
if [ "$EUID" -ne 0 ]
  then echo "Please run as root with sudo."
  exit
fi

# --------------------------------- SSH User --------------------------------- #
echo "Verifying SSH user 'openpod'"

if ! id -u "openpod" >/dev/null 2>&1; then
    echo "Creating user 'openpod'"
    useradd -m -s /bin/bash openpod
    usermod -aG sudo openpod
    mkdir -p ~openpod/.ssh/ && touch ~openpod/.ssh/authorized_keys
    echo "openpod    ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null
else
    echo "User 'openpod' already exists, skipping..."
    mkdir -p ~openpod/.ssh/ && touch ~openpod/.ssh/authorized_keys
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

# ---------------------------- Pillow Requirements --------------------------- #
REQUIRED_PKG="libjpeg-dev"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install libjpeg-dev -y
else
    echo "libjpeg-dev already installed, skipping..."
fi

REQUIRED_PKG="zlib1g-dev"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install zlib1g-dev -y
else
    echo "zlib1g-dev already installed, skipping..."
fi

REQUIRED_PKG="libfreetype6-dev"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install libfreetype6-dev -y
else
    echo "libfreetype6-dev already installed, skipping..."
fi

# -------------------------------- Python 3.11 ------------------------------- #
pytohn_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$pytohn_version" != "3.11" ]; then
    sudo apt install software-properties-common -y
    yes '' | sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get install python3.11 -y
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
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
sudo systemctl stop openpod.service
sudo rm -rf /opt/OpenPod

# ------------------------------- Clone OpenPod ------------------------------ #
set -e # Exit when any command fails.
sudo mkdir -p /opt
cd /opt
sudo git clone --single-branch --branch $BRANCH "${REPO}".git
cd OpenPod

# ----------------------------- Setup Enviroment ----------------------------- #
sudo python3.11 -m venv /opt/OpenPod/env
source /opt/OpenPod/env/bin/activate
pip install --no-input -U -r /opt/OpenPod/requirements.txt

# ---------------------------- Create Directories ---------------------------- #
sudo mkdir -p /opt/OpenPod/logs
sudo mkdir -p /opt/OpenPod/data

# ------------------------------- Create Files ------------------------------- #
# Log Location
sudo touch /opt/OpenPod/logs/RecursionLog.log
sudo touch /opt/OpenPod/logs/System.Snapshot

# Data Location
sudo touch /opt/OpenPod/data/dump.json
sudo touch /opt/OpenPod/data/nodes.json
sudo touch /opt/OpenPod/data/owners.json
sudo touch /opt/OpenPod/data/permissions.json

# ------------------------------- Hardware Info ------------------------------ #
hw_controller=$(grep Hardware < /proc/cpuinfo | cut -d ' ' -f 2)
hw_revision=$(grep Revision < /proc/cpuinfo | cut -d ' ' -f 2)
hw_serial=$(grep Serial < /proc/cpuinfo | cut -d ' ' -f 2)
hw_model=$(grep Model < /proc/cpuinfo | cut -d ' ' -f 2)

# -------------------------------- system.json ------------------------------- #
sudo touch /opt/OpenPod/system.json
serial_uuid=$(cat /proc/sys/kernel/random/uuid)
serial=${serial_uuid//-}
xbee_uuid=$(cat /proc/sys/kernel/random/uuid)
openpod_version=$(git rev-parse HEAD)
echo '{
    "uuid": "'"$serial_uuid"'",
    "debug": '$DEBUG',
    "serial": "'"$serial"'",
    "timezone": "UTC",
    "url": "'"$URL"'",
    "api_url": "'"$API_URL"'",
    "XBEE": {
        "KY": "'"$xbee_uuid"'",
        "OP": false
    },
    "GPIO": {
        "LED_IO": 23,
        "LED_STAT": 17
    },
    "version": "'"$openpod_version"'",
    "OpenPod": {
        "repo": "'"$REPO"'",
        "branch": "'"$BRANCH"'",
        "commit": "'"$openpod_version"'"
    },
    "Hardware": {
        "controller": "'"$hw_controller"'",
        "revision": "'"$hw_revision"'",
        "serial": "'"$hw_serial"'",
        "model": "'"$hw_model"'"
    }
}' > /opt/OpenPod/system.json

# --------------------------- Create Version Folder -------------------------- #
mkdir -p /opt/OpenPod/versions/"$openpod_version"
sudo cp -a /opt/OpenPod/openpod/. /opt/OpenPod/versions/"$openpod_version"/
sudo rm -rf /opt/OpenPod/openpod

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

ExecStart   =   /bin/bash -c "exec /opt/OpenPod/env/bin/python3.11 \\
                /opt/OpenPod/versions/\$(jq '.version' /opt/OpenPod/system.json | xargs)/pod.py"

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now openpod.service
sudo systemctl daemon-reload

echo "- OpenPod is now installed -"
echo "Serial: $serial"
exit 0
