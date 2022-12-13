# Raspberry Pi Setup

This is a guide to help you configure a Raspberry Pi for OpenPod from scratch.

## Compatibility

| Pi Model | Compatible |
|:--------:|:----------:|
|   Pi 3   |    Yes     |
|   Pi 4   |    Yes     |

## Micro SD Card

[Recommended Micro SD Card](https://www.samsung.com/us/computing/memory-storage/memory-cards/evo-plus-microsdxc-memory-card-64gb-mb-mc64ha-am/)

Several considerations were taken into account when selecting the SD card, ultimately, longer-term reliability became the driving factor. The only compromise being made is a slightly reduced boot time which seemed negligible for a device intended always to be on.

Key metrics for SD card comparison:

- Application performance class (A1 & A2), A1 preferred
- [SD Card Comparison](https://techreport.com/forums/viewtopic.php?t=121152)

## Operating System (OS)

[32-bit for Pi3 and 64-bit for 4+](https://ubuntu.com/blog/how-to-install-ubuntu-with-the-new-raspberry-pi-imager)

Each Pod is installed with the latest version of Ubuntu, and the systems are tested daily for compatibility with the latest releases. An image of the OS with the code ready for deployment can make a quick installation.
