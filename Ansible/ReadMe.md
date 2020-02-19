# Ansible Playbooks

This folder contains Ansible Playbooks which are comparable to bash-scripts with additional features. They make it easy to run commands such as "apt install" on many servers simultaneously.

To get started, adapt the inventory.ini to your needs. It contains a list of all servers, allows groups and much more. After that, you can run the Playbooks. For example, installing utilities such as vim (see utilities.yaml) on all servers is as easy as:

```bash
# run ansible playbook called utilities.yaml
ansible-playbook utilities.yaml -i inventory.ini
```



This folder contains the following Playbooks:

- utilities.yaml
  --> Installs basic tools such as vim, nmap and git
- docker.yaml
  --> Installs docker + docker-compose  using the installation script (only RPi)
- swarm.yaml (doesn't work reliably yet!)
  --> Initialized a Swarm based on the groups [docker_swarm_manager] and [docker_swarm_workers] in the inventory.ini