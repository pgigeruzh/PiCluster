# Install Raspbian

Raspbian is the official supported Raspberry Pi OS and can be downloaded from: www.raspberrypi.org/downloads/raspbian/

1. Burn image onto SD card e.g. with etcher: www.balena.io/etcher/
2. Start Raspberry Pi and configure through raspi-config

```bash
# open raspi-config
sudo raspi-config

# change hostname:
# 2. Network Options --> N1 Hostname

# enable ssh:
# 5. Interfacing Options --> P2 SSH

# expand filesystem:
# 7. Advanced Options --> A1 Expand Filesystem

# reboot
sudo reboot
```
