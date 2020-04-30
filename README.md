# Master Project Raspberry Pi Cluster
This repo contains the following:

| Directory  | Description                                                                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Ansible    | Ansible scripts to automate the setup and installation process of the Raspberry Pi's. You only need Ansible and a SSH connection to all Pi's. |
| Benchmarks | A description of the benchmarks used to test the Spark cluster. Furthermore, the experimental data and the analysis can also be found here.   |
| Doc        | Documentation of the project                                                                                                                  |
| Exercises     | Python (PySpark) exercises for the Big Data Analytics lecture.                                                                               |
| Spark      | Python (PySpark) examples that can be run on the Spark cluster.                                                                               |

# Quickstart

First, you have to install [Raspbian](www.raspberrypi.org/downloads/raspbian/) on all Raspberry Pi e.g. using [Etcher](www.balena.io/etcher/). Then, you have boot the Raspberry Pi, set a **unique hostname and IP address** (if the router supports it, we recommend to fix the DHCP address instead of a static IP for portability reasons) and **enable ssh**. It is currently not possible to change the hostname without booting the Raspberry Pi which is why the steps can't be automated.

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

For setting up the Raspberry Pi cluster with **Docker Swarm + GlusterFS** automatically, you have to install **Ansible** on your PC and adjust the inventory.ini file to your needs (instructions [here](https://github.com/pgigeruzh/PiCluster/tree/master/Ansible)). Afterward, you should be able to run the provided Ansible scripts. Please note that the Raspberry Pi is not very robust which means that the scripts can fail (e.g. timeout). If this happens, just re-run the script. In case a Raspberry Pi does not reboot correctly (happens often), disconnect/reconnect power and wait for Ansible to finish. Some scripts might take a long time (20 minutes) to finish because the Raspberry Pi is rather slow.

```bash
# install utilities such as vim/git
ansible-playbook utilities.yaml -i inventory.ini
# install Docker
ansible-playbook docker.yaml -i inventory.ini
# initializes Docker Swarm + GlusterFS
ansible-playbook swarm.yaml -i inventory.ini
```

Now, connect to your Swarm manager and check if your cluster is up and running. 

```bash
# check swarm using command line
docker node ls
docker service ls

# check swarm using a visualizer on port 80
docker service create --name=viz --publish=80:8080/tcp --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock alexellis2/visualizer-arm:latest

# kill the visualizer service
docker service rm viz
```

Last but not least, you can deploy **Spark** on your Raspberry Pi cluster (detailed instructions [here](https://github.com/pgigeruzh/spark)). Adjust the parameters (e.g. --replicas 4) to your needs. Now, you have access to JupyterLab on port 8888 and Spark on port 8080. The practical exercises can be found [here](https://github.com/pgigeruzh/PiCluster/tree/master/Exercises).

```bash
# create an attachable overlay network
docker network create -d overlay --attachable spark
```

```bash
# run spark master
# (first run might take about 10 minutes because it has to download the image)
docker service create --name sparkmaster --network spark --constraint=node.role==manager --publish 8080:8080 --publish 7077:7077 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.master.Master
```

```bash
# run spark workers
docker service create --replicas 4 --replicas-max-per-node 1 --name sparkworker --network spark --publish 8081:8081 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.worker.Worker spark://sparkmaster:7077
```

```bash
# run jupyter lab
docker service create --name jupyterlab --network spark --publish 8888:8888 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password='' --notebook-dir='/gfs'
```

