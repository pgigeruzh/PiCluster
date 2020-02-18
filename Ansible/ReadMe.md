# Ansible Playbooks

This folder contains Ansible Playbooks which can be used to automatically install applications on servers defined in inventory.ini

For example, installing utilities such as vim (see utilities.yaml) on all servers is as easy as:

```bash
# run ansible playbook called utilities.yaml
ansible-playbook utilities.yaml -i inventory.ini
```
