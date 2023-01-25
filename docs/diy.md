# Build Your Own Pod (DIY)

OpenPod was designed to work on off the shelf hardware. The goal is to make it easy to build your own pod. The following instructions will guide you through the process of building your own pod.

These instructions assume you have some basic knowledge of using a Raspberry Pi and interacting with a Linux terminal. If you get stuck or have questions, feel free to reach out to us on [Discord](https://discord.gg/KnFp4jd9AV).

*Ready to go Pods can also be purchased from [Recursion.Space](https://recursion.space/)*

## Parts List

The required parts listed are the minimal hardware resources required to get the core functions of OpenPod running. The optional parts are not required, but are recommended for a better user experience.

### Required Parts

| Part                               | Tested Versions |
|:-----------------------------------|:----------------|
| Raspberry Pi                       | 3B+             |
| Micro SD (Adapter may be required) | 16GB            |
| Power Supply                       | 5V 2.5A         |
| XBee Module                        | 2               |
| SparkFun XBee Explorer USB         | WRL-11812       |
| USB A to USB Mini-B                | N/A             |

### Optional Parts

| Part      | Tested Versions |
|:----------|:----------------|
| Red LED   | N/A             |
| Green LED | N/A             |

## SD Card Setup

We have found a 32-bit version of Ubuntu to be very reliable and easyily installed with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). With the imager open navigate to `CHOOSE OS > Other general-purpose OS > Ubuntu > Ubuntu Server 22.10 (32-bit)`, finally select the SD card and click `WRITE`.

*Note: While OpenPod will work on any version of Linux that Raspberry Pi supports, including versions with a GUI, it is recommended to use a headless version of Linux.*

## Installing OpenPod

Once the SD card is flashed and loaded into the Raspberry Pi, connect the Pi to your network via ethernet and optionally to a monitor and keyboard before powering on.

The Pi will boot and you will be prompted to login. The default username is `ubuntu` and the password is `ubuntu`. Once logged in, run the following commands to install OpenPod:

```bash
sudo wget -qO- https://openpod.recursion.space | bash /dev/stdin
```

**Important: When installation is complete make sure note the serial that is printed on the screen. This is how you will link it to your Recursion account. If you forget to copy this down it can be found in the file `/opt/OpenPod/system.json`**

### Optional Configurations

To help easily identify the Pod on your network, or differentiate it from other Raspberry Pi's you may have, we recommended changing the hostname. To do this, run the following command:

```bash
sudo nano /etc/hostname
```

Change the hostname to something unique, then press `CTRL+X` to exit and save the changes before rebooting the Pi.

## Linking to Recursion.Space

With OpenPod successfully installed, you can now link it to your Recursion account. To do this, navigate to the [Recursion.Space](https://recursion.space/) website and login as a space owner. Look for `Pods` in the menu then the `Pod Configuration` tab and finally the `+ Pod` button where you will be prompted for a Pod name and the serial number you noted during installation.
