<div align="center">

# OpenPod

[![CI | E2E Integration](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_E2E.yml/badge.svg)](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_E2E.yml)
&nbsp;
[![CI | Pylint](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_Pylint.yml/badge.svg)](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_Pylint.yml)
&nbsp;
[![CI | Script Check](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_ShellCheck.yml/badge.svg)](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_ShellCheck.yml)
&nbsp;
[![CI | Build & Test](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_Tests.yml/badge.svg)](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_Tests.yml)
&nbsp;
[![CI | Installer](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_TestInstaller.yml/badge.svg)](https://github.com/RecursionSpace/OpenPod/actions/workflows/CI_TestInstaller.yml)

</div>

- [OpenPod](#openpod)
  - [What is OpenPod?](#what-is-openpod)
  - [Installation](#installation)
- [Software Design](#software-design)
- [Development](#development)
- [Initialization](#initialization)
- [MQTT](#mqtt)
- [Updates](#updates)
- [Logging](#logging)
  - [Repository Directory Structure](#repository-directory-structure)
  - [Deployed Directory Structure](#deployed-directory-structure)
- [Community and Contributing](#community-and-contributing)

## What is OpenPod?

The “Pod” is the physical extension of the Recursion.Space system for a facility. The Pod allows for door/egress and equipment control nodes. Additionally, the Pod acts as a local backup in an internet outage for users to continue accessing their facility. The Pod has a direct internet connection then uses a wireless method to communicate with nodes. A single facility can have multiple Pods, but each Pod can only be linked to one facility.

*Note: Versioning follows the [Semantic Versioning 2.0.0 standard](https://semver.org/)*

## Installation

OpenPod is designed to communicate with hardware over a local mesh network using [XBee module](https://www.digi.com/products/embedded-systems/digi-xbee/rf-modules/2-4-ghz-rf-modules/xbee3-zigbee-3). While OpenPod can be installed on any computer running Ubuntu, most installations are done on a [Raspberry Pi](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/). To prepare a Raspbery Pi for OpenPod checkout the [Pi Setup Guide](docs/pi_setup.md).

For convenience, an installation script as been provided that will download OpenPod and make the necessary system changes to get OpenPod running. This script can be run from the command line using the following command:

```bash
sudo wget -qO- https://openpod.recursion.space | bash /dev/stdin [options] [arguments]
```

| Option Flag | Description               | Example                                                                            |
|:-----------:|---------------------------|------------------------------------------------------------------------------------|
|     -h      | Help                      | sudo wget -qO- openpod.recursion.space \| bash /dev/stdin -h                       |
|     -d      | Enable Debug Installation | sudo wget -qO- openpod.recursion.space \| bash /dev/stdin -d                       |
|     -u      | Set Custom URL endpoint   | sudo wget -qO- openpod.recursion.space \| bash /dev/stdin -u stage.recursion.space |

\*No supported arguments are currently supported.

# Software Design

The embedded code manages the communication between the API server and the node communication, acting as a middleman. There needs to be minimal factory configuration to make deployable units quickly.

1) Assume the Pod is plug and play internet connection. (DHCP)
2) Pods can self-generate ID and register it with the central system.
3) Users enter an ID to link the physical Pod with the web interface.

Pod communicates to the web API via hook notifications, and a return confirmation is sent back.

- Records Door/Equipment access
- Registers new nodes and Pods
- Pulls info dumps

The web interface communicates with the Pod via MQTT.

- Alerts for new users
- User updates
- Remote control (door unlock)

Each Pod is on its MQTT topic, and the topic is created once the Pod registers with the central system.

# Development

Pod software development is done on a DigitalOcean hosted server. It is then transferred to the physical hardware running the system and tested before going into production.

# Initialization

Pod uses an initializer or “launcher” to configure the system before running the main code. The launcher performs the following tasks before running the main program:

- Update & Upgrade the OS
- [Sync Clock](https://vitux.com/keep-your-clock-sync-with-internet-time-servers-in-ubuntu/)
- Installs program required packages
- Check for required files, create them if missing
- Configure start on boot file
- Creates serial if needed
- Registers the Pod with the API server
- Initializes the main program under [/opt/](https://unix.stackexchange.com/questions/11544/what-is-the-difference-between-opt-and-usr-local)

To launch the software, when the device boots, the launcher configures the system first to run the software in the [background](https://janakiev.com/blog/python-background/) and then creates a script that executes the launch on [startup](https://askubuntu.com/questions/817011/run-python-script-on-os-boot). Working version with a [cronjob](https://www.linuxbabe.com/linux-server/how-to-enable-etcrc-local-with-systemd).

```bash
(@reboot (cd /home/ubuntu/RecursionHub &&  sudo python3 HUB_Launcher.py &))
```

# MQTT

The MQTT protocol is used for server to Pod communication, allowing the Pod to listen in real-time for incoming instruction.

Communication to Pods is accomplished from quick commands represented by a hexadecimal number.

| Command Number | Command               |
|----------------|-----------------------|
| AA (170)       | Facility ID Available |
| BA (186)       | Pull User Dump        |
| CA (202)       | Update Available      |
| DA(218)        | Time Zone Change      |
|                |                       |
| FA (250)       | Zip & Send Logs       |

# Updates

The end-user triggers updates via the web server to run them with minimal interruption. An MQTT message is sent to the Pod to initiate the updating process. The update is a zip file downloaded from the [server](https://stackoverflow.com/questions/38697529/how-to-return-generated-file-download-with-django-rest-framework).

1) Download zip file from server and store in the update folder.
2) Unzip contents of a zip file
3) Run Launcher

First, commit and push the latest changes to git to prepare an update. Using WinSCP, download the 0_1_0 folder with the newest code. Rename the downloaded folder to match the latest version number. Zip the folder's CONTENTS, so there is no second directory folder with a matching name inside the zip file folder. Clean up all extra copies of the old folder. Update the latest version name using the recursion admin panel, then update their devices.

# Logging

The Recursion System uses several logging points to be used both for troubleshooting as well as security and auditing. There are two log files created for the Pod, RecursionLog.log, and TransactionLog.log; each one is used as follows:

**RecursionLog.log** is used to record system events.

- Coming online
- Updating
- New Nodes being added
- Nodes coming online

**System.Snapshot** file contains a JSON summary of the Pod for debugging purposes. The information available in this file must also be readily accessible from the server for troubleshooting purposes.

```json
{
    "local_ip": "xx.xx.xx.xx",
}
```

## Repository Directory Structure

```default
.
├── .github             # CI/CD using GitHub Actions and other functions.
├── tests               # Contains unit testing files.
└── openpod             # Contains OpenPod functionality.
    └── modules         # Independent core functions.
```

## Deployed Directory Structure

```default
OpenPod/
|--------- Version A/
	|--------- HUB.py
    |--------- HUB_Launcher.py
    |--------- HUB_Updater.py
    |----------settings.py
    |--------- modules/

|--------- logs/
	|--------- RecursionLog.log
	|--------- TransactionLog.log

|--------- data/
	|-------- dump.json
	|-------- owners.json
	|-------- nodes.json
	|---------permissions.json

|--- system.json

```

# Community and Contributing

OpenPod is developed by [Recursion.Space](https://recursion.space/) and by users like you. We welcome both pull requests and issues on [GitHub](https://github.com/RecursionSpace/OpenPod). Bug fixes and new protocols are encouraged.

<div align="center">

<a target="_blank" href="https://discord.com/invite/KnFp4jd9AV">![Discord Banner 2](https://discordapp.com/api/guilds/790311269420630079/widget.png?style=banner2)</a>

</div>
