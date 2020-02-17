# Use QEMU to emulate Raspbian (ARM) on a PC (x86)

The following instructions are specifically for Ubuntu 18.04. The process should be similar on other operating systems, however, there are some problems to consider. At the time of writing, the authors couldn't get it to work on MacOS Catalina. Wireshark revealed that the network bridge (www.tuntaposx.sourceforge.net) wasn't able to receive packages (e.g. DHCP) for unknown reasons. Furthermore, it should be noted that a wifi adapter might not work to setup a bridge.

To emulate Raspbian (official RPi OS), the underlaying ARM architecture needs to be emulated as well. For this reason, a simple virtual machine is not enough. Fortunately, a virtualization software called QEMU (processor emulator) is open-source and freely available.

Using QEMU is quite complicated and may need a lot of patience. The following steps are a guideline for a successful start:

1. Install QEMU: www.qemu.org

   ```bash
sudo apt install qemu bridge-utils ifupdown
   ```
   
2. Download Raspbian Buster Lite: www.raspberrypi.org/downloads/raspbian/

   Download "kernel-qemu-4.19.50-buster" and "versatile-pb.dtb" from: www.github.com/dhruvvyas90/qemu-rpi-kernel/

   Place everything you have downloaded into one folder. It should include these files:

   ```
   - 2020-02-05-raspbian-buster-lite.img
   - versatile-pb.dtb
   - kernel-qemu-4.19.50-buster
   ```

7. Resize Raspbian

   ```bash
   qemu-img convert -f raw -O qcow2 2020-02-13-raspbian-buster-lite.img 2020-02-13-raspbian-buster-lite.qcow2
   
   qemu-img resize 2020-02-13-raspbian-buster-lite.qcow2 +5G
   ```

4. Setup Bridge

   ```bash
   # find your network device e.g. ethernet enp0
   ip a
   
   # open configuration file
   sudo vim /etc/network/interfaces
   # add the following lines to create a bridge "br0" on "enp0" and save
   iface enp0 inet manual
   iface br0 inet dhcp
           bridge_ports enp0s25
   
   # setup qemu bridge helper
   sudo chmod u+s /usr/lib/qemu/qemu-bridge-helper
   sudo mkdir /etc/qemu
   
   # open configuration file for qemu-bridge-helper
   sudo vim /etc/qemu/bridge.conf
   # add the following line and save
   allow br0
   ```

5. Start QEMU VM

   (Change the mac for every new machine!)

   ```bash
   # start bridge (only once)
   sudo ifup br0
   
   # start vm
   sudo qemu-system-arm \
   	--kernel kernel-qemu-4.19.50-buster \
   	--dtb versatile-pb.dtb \
   	--m 256 -cpu arm1176 \
   	--machine versatilepb \
   	--hda 2020-02-13-raspbian-buster-lite.qcow2 \
   	--append "root=/dev/sda2" \
   	--display none \
   	--serial stdio \
   	--no-reboot \
   	--netdev bridge,id=hn0,helper=/usr/lib/qemu/qemu-bridge-helper \
   	--device virtio-net-pci,netdev=hn0,id=nic1,mac=00:00:00:00:00:01
   ```

6. Configure Raspbian

   ```bash
   # enable ssh
   sudo systemctl enable ssh
   sudo systemctl start ssh
   
   # enlarge swap by opening /etc/dphys-swapfile
   sudo nano /etc/dphys-swapfile
   # change this line (RAM is limited to 256MB due to QEMU)
   CONF_SWAPSIZE=1024
   # apply new settings
   sudo /etc/init.d/dphys-swapfile stop
   sudo /etc/init.d/dphys-swapfile start
   
   # resize disk by going to: Advanced Options --> Expand Filesystem
   cp /usr/bin/raspi-config ~
   sed -i 's/mmcblk0p/sda/' ~/raspi-config
   sed -i 's/mmcblk0/sda/' ~/raspi-config
   sudo ~/raspi-config
   
   # apply changes by rebooting
   sudo reboot
   ```
