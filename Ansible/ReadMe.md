# Ansible

Ansible (www.ansible.com) is an open-source tool for server configuration. It simplifies automation and is especially useful when multiple-servers need to be setup. The only requirement is to have Ansible installed on a "master" and ssh open on all "slaves". The docs are available here: https://docs.ansible.com

To install Ansible, follow the docs for your operating system. In Ubuntu 18.04, it is as follows:

```bash
sudo apt update
sudo apt install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt update
sudo apt install ansible
```

Now that Ansible is installed, you need to accept the ssh keys of all servers. This can be done by opening an ssh connection with every server.

```bash
# ssh connection (or add finterprints)
ssh pi@192.168.2.209
ssh pi@192.168.2.210
...
```

Last but not least, you need to adapt the inventory.ini to your needs. It contains a list of all servers, allows groups and much more.

```bash
# edit inventory.ini and add all servers you want to connect to
raspberrypi0 ansible_host=192.168.2.205 ansible_user=pi ansible_ssh_pass=raspberry
raspberrypi1 ansible_host=192.168.2.203 ansible_user=pi ansible_ssh_pass=raspberry
...
```

Now you can run ansible commands on the servers in your inventory:

```bash
# now we can ping all servers with ansible
ansible all -m ping -i inventory.ini

# or run some shell commands
ansible all -m shell -a "hostname"
ansible all -m shell -a "df -h"

# or reboot
ansible all -m reboot -i inventory.ini
```

# Ansible Playbooks

Ansible Playbooks are comparable to bash-scripts with additional features. They make it easy to run a list of commands such as "apt install" on many servers simultaneously.

This folder contains the following Playbooks:

- utilities.yaml
  --> Installs basic tools such as vim, nmap and git
- docker.yaml
  --> Installs docker + docker-compose  using the installation script (only RPi)
- swarm.yaml
  --> Initialized a Swarm based on the groups [docker_swarm_manager] and [docker_swarm_workers] in the inventory.ini

Running the Playbooks is straight forward. For example, executing utilities.yaml (installs vim, nmap, git...) is as easy as:

```bash
# run ansible playbook called utilities.yaml
ansible-playbook utilities.yaml -i inventory.ini
```
