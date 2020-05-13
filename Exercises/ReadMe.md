# Exercises

These exercises are based on the following hostnames and IP addresses. Please adjust them to your specific hardware setup.
| Hostname                                | IP Address    |
| --------------------------------------- | ------------- |
| cluster1raspberry0 (**master**/manager) | 192.168.2.250 |
| cluster1raspberry1 (**slave**/worker)   | 192.168.2.251 |
| cluster1raspberry2 (**slave**/worker)   | 192.168.2.252 |
| cluster1raspberry3 (**slave**/worker)   | 192.168.2.253 |



## Cluster Setup

<div align="center">
  <a href="https://www.youtube.com/watch?v=-xZRUxrKbsY">
    <img src="images/setup.png" alt="PiCluster Setup" style="width:40%;">
  </a>
</div>


First, you have to install [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on all Raspberry Pi e.g. using [Etcher](https://www.balena.io/etcher/). Then, you have boot the Raspberry Pi, set a **unique hostname and IP address** (if the router supports it, we recommend to fix the DHCP address instead of a static IP for portability reasons) and **enable ssh**. It is currently not possible to change the hostname without booting the Raspberry Pi which is why the steps can't be automated.

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

For automatically setting up the Raspberry Pi cluster with **Docker Swarm + GlusterFS**, you need **Ansible** and an **ssh connection to all Raspberry Pi**. The Ansible scripts together with a short instruction can be found [here](https://github.com/pgigeruzh/PiCluster/tree/master/Ansible). In summary, you have to **change the inventory.ini** file to fit your specific hardware setup and **run the Ansible scripts** as shown below. Please note that the Raspberry Pi is not very robust which means that the scripts can fail (e.g. timeout). If this happens, just re-run the script. In case a Raspberry Pi does not reboot correctly (happens often), disconnect/reconnect power and wait for Ansible to finish. Some scripts might take a long time (20 minutes) to finish because the Raspberry Pi is rather slow.

```bash
# install utilities such as vim/git
ansible-playbook utilities.yaml -i inventory.ini
# install Docker
ansible-playbook docker.yaml -i inventory.ini
# initializes Docker Swarm + GlusterFS
ansible-playbook swarm.yaml -i inventory.ini
```



## Service Deployment (Visualizer, Spark, JupyterLab)

<div align="center">
  <a href="https://www.youtube.com/watch?v=Tj-Rb9JvQ7w">
    <img src="images/deployment.png" alt="PiCluster Service Deployment" style="width:40%;">
  </a>
</div>



To deploy a service on your cluster, you have to **use ssh and connect to your master** (192.168.2.250) because services can't be deployed on a worker node. First, it is useful to deploy a monitoring tool called **Visualizer** as shown below. Because of the port mapping (--publish), you can directly access the Visualizer from any browser (visit 192.168.2.250:80).

```bash
# deploy Visualizer on port 80 and constrain it to the master
docker service create --name=viz --publish=80:8080/tcp --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock alexellis2/visualizer-arm:latest

# kill the visualizer if needed
docker service rm viz
```

Now you can deploy **Spark** with the commands below (detailed instructions [here](https://github.com/pgigeruzh/spark) if needed). Adjust the parameters (e.g. --replicas 4) to your needs. The Spark UI can be accessed on port 8080 (visit 192.168.2.250:8080).

```bash
# create an attachable overlay network
# (all spark containers have to be within the same network to be able to connect)
docker network create -d overlay --attachable spark
```

```bash
# run spark master
# (first run might take about 10 minutes because it has to download the image on all RPi)
docker service create --name sparkmaster --network spark --constraint=node.role==manager --publish 8080:8080 --publish 7077:7077 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.master.Master
```

```bash
# run spark workers
# (runs four workers and mounts gluster at /gfs to synchronize files accross all nodes)
docker service create --replicas 4 --replicas-max-per-node 1 --name sparkworker --network spark --publish 8081:8081 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.worker.Worker spark://sparkmaster:7077
```

Last but not least, you can deploy JupyterLab on port 8888 (visit 192.168.2.250:8888) as shown below.

```bash
# run jupyter lab
# (constraint to the manager because it mounts the docker socket)
docker service create --name jupyterlab --network spark --constraint=node.role==manager --publish 8888:8888 --mount source=gfs,destination=/gfs --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock -e SHELL=/bin/bash pgigeruzh/spark:arm jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password='' --notebook-dir='/gfs'
```

In summary, you should have the following services up and running.

| Service    | URL                |
| ---------- | ------------------ |
| Visualizer | 192.168.2.250:80   |
| Spark UI   | 192.168.2.250:8080 |
| JupyterLab | 192.168.2.250:8888 |

For managing your cluster, the following commands might be useful:

```bash
# list all services
docker service ls

# remove a service
docker service rm your-service-name
```



## Introduction to Spark

Visit JupyterLab (192.168.2.250:8888) and run [this](https://github.com/pgigeruzh/PiCluster/blob/master/Exercises/template.ipynb) template. You should see the output: "Pi is roughly 3.156360". If you prefer to use spark-submit, you can do so in the terminal. Please note that **all files should be stored in /gfs** because the folder is synced across all nodes.

In case you're not familiar with the Pyspark syntax and the foundations of Spark RDD's and Dataframes, just have a look on
[this](https://github.com/pgigeruzh/PiCluster/blob/master/Exercises/Movielens_exercises.ipynb) Jupyter Notebook. This should provide you a guided introduction to some basic operations in Spark based on the Movielens Dataset. 

The provided Movielens exercise will help you to:
*  Read and understand the schema of our Movielens dataset
*  Calculate summary statistics
*  Learn how to perform joins and aggregations using PySpark
*  Understand fundamental RDD transformations like **map(), flatMap() or reduceByKey()**

This will give you the possibility to write your own code for testing the resilience of the cluster in the next exercise. Of course, you can adapt the provided examples and try to write codes, which need high computational resources to process the results. 


## Testing Resilience

<div align="center">
  <a href="https://www.youtube.com/watch?v=4scaV421mQo">
    <img src="images/resilience.png" alt="PiCluster Resilience" style="width:40%;">
  </a>
</div>

For testing the resilience of the cluster, you can try your own code or use the template below. The template calculates the mean, standard deviation, min, max, and count of the rating columns and parallelizes well. Other tasks might not parallelize well, hence, they do not profit from additional workers.

```python
import time
start_time = time.time()

from pyspark.sql import SparkSession

if __name__ == "__main__":

    print("--- start ---")

    # Connect to the master
    spark = SparkSession\
        .builder\
        .master("spark://sparkmaster:7077")\
        .appName("resilience") \
        .getOrCreate()

    # Calculate count, mean, sd, min, max of ratings
    ratings = spark.read.csv('ml-20m/ratings.csv', inferSchema=True, header=True)
    ratings.describe().show()

    # Disconnect
    spark.stop()

    print("Duration: %s seconds" % (time.time() - start_time))
    print("--- end ---")
```
First, check JupyterLab, Spark UI, and Visualizer. Make sure that your cluster is in working condition. Afterward, open JupyterLab and create a new notebook. **Run the template above** (or your own code) and visit Spark UI. **Check** the **number of assigned cores** and the **duration**. If something goes wrong, you can kill the task in Spark UI but make sure to restart the IPython kernel. If everything works as expected, you should see a table with descriptive statistics and duration (seconds) in your notebook's output. Remember the duration and **disconnect a worker** (or two). Please note that the cluster crashes when master is down or less than two nodes are active. **Wait** until Spark UI highlights the status of the workers as "DEAD" and **re-run the notebook**. Again, **check the assigned cores and the duration**. The duration should now be longer because you have fewer workers. Last but not least, **reconnect the workers**, wait till they are "ALIVE" and **run the notebook again**. The results should be comparable to the first run.

In a second step, you can try to **disconnect the workers while running your notebook**. The notebook should still run to the end but it might take longer because the resources have to be reallocated.
