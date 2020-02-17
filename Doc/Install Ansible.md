# Install Ansible

Ansible (www.ansible.com) is an open-source tool for server configuration. It simplifies automation and is especially useful when multiple-servers need to be setup. The only requirement is to have Ansible installed on a "master" and ssh open on all "slaves". The docs are available here: https://docs.ansible.com

The following instructions are for installing Ansible on Ubuntu 18.04 but should be similar for other operating system:

1. Install Ansible

```bash
sudo apt update
sudo apt install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt update
sudo apt install ansible
```

2. Setup inventory (all machines to connect to)

```bash
# open file
sudo vim /etc/ansible/hosts

# add/change this part
[cluster]
192.168.2.209 ansible_user=pi ansible_ssh_pass=raspberry
192.168.2.210 ansible_user=pi ansible_ssh_pass=raspberry
```

3. Check server connections

```bash
# check ssh connection manually (or add finterprints)
ssh pi@192.168.2.209
ssh pi@192.168.2.210

# now we can ping all servers with ansible
ansible all -m ping

# or run some shell commands
ansible all -m shell -a "hostname"
ansible all -m shell -a "df -h"
```