#!/bin/bash
#
# Installer for OpenPod
# More information: https://github.com/blokbot-io/OpenBlok/blob/master/install.sh

# Steps:
#   1. Parse command-line arguments
#   2. Validate environment and dependencies
#   3. Install OpenPod
#   4. Configure systemd service
#   5. Final checks


# ---------------------------------------------------------------------------- #
#                              Strict Mode & Setup                             #
# ---------------------------------------------------------------------------- #
set -Eeuo pipefail  # Catch unbound variables, errors, and exit the script in case of failure
shopt -s nullglob   # If a glob does not match, return empty string

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (e.g., sudo ./install.sh)."
  exit 1
fi

# Ensure the script runs in a Debian/Ubuntu environment
if ! command -v apt-get &>/dev/null; then
  echo "This script requires a Debian-based system with apt-get."
  exit 1
fi

# Disable interactive prompts
if [ -f /etc/needrestart/needrestart.conf ]; then
  sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
fi
export DEBIAN_FRONTEND=noninteractive


# ---------------------------------------------------------------------------- #
#                                     Help                                     #
# ---------------------------------------------------------------------------- #
usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -h           Display this help and exit"
  echo "  -b <branch>  Set custom branch for OpenPod"
  echo "  -u <url>     Set custom URL for OpenPod"
  echo "  -d           Enable debug mode"
  echo
  echo "Example:"
  echo "  $0 -b release -u recursion.space"
  exit 1
}

# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
DEBUG=false # -d
BRANCH=""   # -b
URL=""      # -u
REPO='https://github.com/RecursionSpace/OpenPod'

PYTHON_VERSION='3.11'
VENV_DIR='/opt/OpenPod/venv'
PYTHON_PATH="$VENV_DIR/bin/python"
# ---------------------------------------------------------------------------- #
#                                    Options                                   #
# ---------------------------------------------------------------------------- #
while getopts ":hb:u:d" opt; do
  case "${opt}" in
    h) # display Help
         usage
         exit;;
    b) # Custom branch
        BRANCH="${OPTARG}";;
    u) # Custom URL endpoint
         URL="${OPTARG}";;
    d) # Enable debug mode
        DEBUG=true ;;
    \?) # Invalid option
         echo "Invalid option: -${OPTARG}" >&2;
         usage ;;
    :) # Missing argument
         echo "Option -${OPTARG} requires an argument." >&2;
         usage
         exit 1 ;;
  esac
done

# If no branch set, default based on debug or release
if [ -z "$BRANCH" ]; then
  if [ "$DEBUG" = true ]; then
    BRANCH='dev-release'
  else
    BRANCH='release'
  fi
fi

# If no URL set, default based on debug or release
if [ -z "$URL" ]; then
  if [ "$DEBUG" = true ]; then
    URL='dev.recursion.space'
  else
    URL='recursion.space'
  fi
fi

# API_URL logic
if [ "$DEBUG" = true ]; then
  API_URL='dev.api.recursion.space'
else
  API_URL='api.recursion.space'
fi

echo "==> Installing OpenPod"
echo "Debug   | $DEBUG"
echo "Repo    | $REPO"
echo "Branch  | $BRANCH"
echo "URL     | $URL"
echo "API_URL | $API_URL"
echo "-----------------------------------------------"

# ---------------------------------------------------------------------------- #
#                                Helper Functions                              #
# ---------------------------------------------------------------------------- #
install_if_needed() {
  local pkg="$1"
  local status
  status=$(dpkg-query -W --showformat='${Status}\n' "$pkg" 2>/dev/null | grep "install ok installed" || true)
  if [ -z "$status" ]; then
    echo "Installing $pkg..."
    apt-get install -y "$pkg"
  else
    echo "$pkg is already installed, skipping..."
  fi
}


# ---------------------------------------------------------------------------- #
#                                 System Checks                                #
# ---------------------------------------------------------------------------- #

# --------------------------------- SSH User --------------------------------- #
if ! id -u "openpod" >/dev/null 2>&1; then
  echo "==> Creating user 'openpod'"
  useradd -m -s /bin/bash openpod
  usermod -aG sudo openpod
  mkdir -p ~openpod/.ssh/
  touch ~openpod/.ssh/authorized_keys
  echo "openpod    ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers >/dev/null
else
  echo "==> User 'openpod' already exists, skipping..."
  mkdir -p ~openpod/.ssh/
  touch ~openpod/.ssh/authorized_keys
fi

# ---------------------------- Update System Time ---------------------------- #
sudo timedatectl set-timezone UTC


# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #
install_if_needed build-essential
install_if_needed chrony
install_if_needed unzip
install_if_needed jq
install_if_needed libjpeg-dev
install_if_needed zlib1g-dev
install_if_needed libfreetype6-dev
install_if_needed software-properties-common


# -------------------------------- Python 3.11 ------------------------------- #
if ! python3.11 --version &>/dev/null; then
  echo "Installing Python 3.11..."
  add-apt-repository ppa:deadsnakes/ppa -y
  apt-get update -y
  apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv
else
  echo "Python 3.11 is already installed."
  # still ensure dev and venv
  install_if_needed python3.11-dev
  install_if_needed python3.11-venv
fi


# ---------------------------------------------------------------------------- #
#                                    OpenPod                                   #
# ---------------------------------------------------------------------------- #

# -------------------------- Clear Previous Install -------------------------- #
if systemctl is-active --quiet openpod.service; then
  systemctl stop openpod.service
fi
rm -rf /opt/OpenPod

# ------------------------------- Clone OpenPod ------------------------------ #
mkdir -p /opt
cd /opt
git clone --single-branch --branch $BRANCH "${REPO}".git
cd OpenPod

# ----------------------------- Setup Environment ---------------------------- #
python${PYTHON_VERSION} -m venv "$VENV_DIR"
$PYTHON_PATH -m pip install --upgrade pip
$PYTHON_PATH -m pip install --no-input -U -r /opt/OpenPod/requirements.txt

# ---------------------------- Create Directories ---------------------------- #
mkdir -p /opt/OpenPod/logs
mkdir -p /opt/OpenPod/data

# ------------------------------- Create Files ------------------------------- #
# Log Location
touch /opt/OpenPod/logs/RecursionLog.log
touch /opt/OpenPod/logs/System.Snapshot

# Data Location
touch /opt/OpenPod/data/dump.json
touch /opt/OpenPod/data/nodes.json
touch /opt/OpenPod/data/owners.json
touch /opt/OpenPod/data/permissions.json

# ------------------------------- Hardware Info ------------------------------ #
hw_controller=$(grep Hardware /proc/cpuinfo | awk '{print $3}')
hw_revision=$(grep Revision /proc/cpuinfo | awk '{print $3}')
hw_serial=$(grep Serial /proc/cpuinfo | awk '{print $3}')
hw_model=$(grep Model /proc/cpuinfo | cut -d':' -f2 | sed 's/^\s*//')

# -------------------------------- system.json ------------------------------- #
system_file="/opt/OpenPod/system.json"
touch "$system_file"

serial_uuid=$(cat /proc/sys/kernel/random/uuid)
serial=${serial_uuid//-}
xbee_uuid=$(cat /proc/sys/kernel/random/uuid)
openpod_version=$(git rev-parse HEAD)

cat <<EOF > "$system_file"
{
  "uuid": "$serial_uuid",
  "debug": $DEBUG,
  "serial": "$serial",
  "timezone": "UTC",
  "url": "$URL",
  "api_url": "$API_URL",
  "XBEE": {
    "KY": "$xbee_uuid",
    "OP": false
  },
  "GPIO": {
    "LED_IO": 23,
    "LED_STAT": 17
  },
  "version": "$openpod_version",
  "OpenPod": {
    "repo": "$REPO",
    "branch": "$BRANCH",
    "commit": "$openpod_version"
  },
  "Hardware": {
    "controller": "$hw_controller",
    "revision": "$hw_revision",
    "serial": "$hw_serial",
    "model": "$hw_model"
  }
}
EOF

# --------------------------- Create Version Folder -------------------------- #
mkdir -p /opt/OpenPod/versions/"$openpod_version"
sudo cp -a /opt/OpenPod/openpod/. /opt/OpenPod/versions/"$openpod_version"/
sudo rm -rf /opt/OpenPod/openpod

# --------------------------- Setup OpenPod Service -------------------------- #
service_file="/etc/systemd/system/openpod.service"
cat <<EOF > "$service_file"
[Unit]
Description=OpenPod | Recursion.Space
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
WorkingDirectory=/opt/OpenPod

ExecStart   =   /bin/bash -c "exec /opt/OpenPod/venv/bin/python \\
                /opt/OpenPod/versions/\$(jq '.version' /opt/OpenPod/system.json | xargs)/pod.py"

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable openpod.service
systemctl start openpod.service

echo "==> OpenPod is now installed."
echo "    Serial: $serial"
exit 0
