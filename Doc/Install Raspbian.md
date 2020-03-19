# Install Raspbian

Raspbian is the official supported Raspberry Pi OS and can be downloaded from: www.raspberrypi.org/downloads/raspbian/

1. Burn image onto SD card e.g. with etcher: www.balena.io/etcher/

2. Start Raspberry Pi and configure through raspi-config

   (it is currently not possible to change the hostname without booting the raspberry)

```bash
# open raspi-config
sudo raspi-config

# change hostname:
# 2. Network Options --> N1 Hostname

# enable ssh:
# 5. Interfacing Options --> P2 SSH

# reboot
sudo reboot
```

3. Fix IP address (we recommend using a fixed DHCP IP instead of a static IP for portability reasons)
