# Deploy Spark on Docker Swarm (RPi)

To deploy spark on docker swarm, you first need to have a "Spark" docker image. The few options available are for x86 and not arm, therefore, you need to either 1) create your own or 2) build/compile an existing one yourself. We have decided to go with the latter one. It needs to be noted that, at the time of writing this article, Raspian is still 32 bit and can therefore not run arm64 images.

First, connect to your swarm master. Then, clone this git repo: www.github.com/gettyimages/docker-spark.git. It contains a Dockerfile for running Spark and works on arm too. Then, build the docker image and name it "dockerized-spark". 

(Caution: The image needs to be built on every raspberry in the cluster! Otherwise, the error "No such image" occurs.)

```bash
# connect to swarm master
ssh pi@192.168.2.205

# clone repo
git clone https://github.com/gettyimages/docker-spark.git
cd docker-spark

# build image
docker build -t docker-spark .
# check available docker images
docker images
```

To deploy it on a Swarm, you need to:

```bash
# label nodes to be able to distribute work manually
docker node update --label-add type=sparkmaster raspberrypi0
docker node update --label-add type=sparkworker raspberrypi1

# create an attachable overlay network
docker network create -d overlay --attachable spark

# run spark master
docker service create --name sparkmaster --network spark --constraint node.labels.type==sparkmaster --publish 8080:8080 --publish 7077:7077 docker-spark bin/spark-class org.apache.spark.deploy.master.Master
# run spark workers
docker service create --replicas 2 --name sparkworker --network spark --constraint node.labels.type==sparkworker --publish 8081:8081 docker-spark bin/spark-class org.apache.spark.deploy.worker.Worker spark://sparkmaster:7077
```

To see if it worked, visit the ip of your Swarm master e.g.192.168.2.205:8080
Furthermore, you can run:

```bash
# command line
docker service ls

# visualizer on port 80
docker service create --name=viz --publish=80:8080/tcp --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock alexellis2/visualizer-arm:latest

# for debugging purposes, a standard webserver might be useful as well
# (it should be available on every node on port 81)
docker service create --name nginx --replicas 2 --publish published=81,target=80 nginx

# run an example with "spark-submit"
# (you need to be in the overlay networktherefore it won't work from outside the cluster)
docker run --net=spark docker-spark spark-submit --master spark://sparkmaster:7077 /usr/spark-2.4.1/examples/src/main/python/pi.py
# or run your own code
# (you need to mount your code as a volume with -v)
docker run -v /home/pi/:/data --net=spark --rm docker-spark spark-submit --master spark://sparkmaster:7077 /data/pi.py
```

# Persistent Storage with GlusterFS

Spark requires data and by default, it uses hdfs (hadoop file system). However, docker swarm does not persist container data. For this reason, I use GlusterFS (www.gluster.org) to share data between different nodes. Together with a docker plugin (www.github.com/trajano/docker-volume-plugins/tree/master/glusterfs-volume-plugin), it is possible to mount these shared volumes directly, hence, a hdfs is not required.

First, glusterfs needs to be installed and configured on every node. This step is unrelated to docker. The following example is for installing glusterfs on two nodes (192.168.2.202, 192.168.2.203):

```
# install glusterfs (all servers)
sudo apt-get install glusterfs-server -y
sudo systemctl start glusterd
sudo systemctl enable glusterd
systemctl status glusterd
sudo mkdir --parents /glusterfs/distributed

# probe peers (replace sample ip with servers)
sudo gluster peer probe 192.168.2.202
sudo gluster pool list

# create volume
sudo gluster volume create gfs replica 2 192.168.2.202:/glusterfs/distributed 192.168.2.203:/glusterfs/distributed force

# start volume
sudo gluster volume start gfs
sudo gluster volume info gfs
```

Now, glusterfs is running with a shared folder on /glusterfs/distributed. The next step is to install a docker plugin to be able to connect docker volumes with gluster volumes. This step needs to be done an all nodes.

```
# install docker volume plugin (all servers)
docker plugin install --alias gluster \
  jmb12686/glusterfs-volume-plugin \
  --grant-all-permissions --disable
docker plugin set gluster SERVERS=192.168.2.202,192.168.2.203
docker plugin enable gluster
docker volume create --driver gluster gfs
```

Last but not least, the newly created docker volume (gfs) can be attached to containers e.g. Spark:

```
# run spark workers
docker service create --replicas 2 --name sparkworker --network spark --constraint node.labels.type==sparkworker --publish 8081:8081 --mount source=gfs,destination=/gfs docker-spark bin/spark-class org.apache.spark.deploy.worker.Worker spark://sparkmaster:7077

# to copy a file to glusterfs, mount the volume and run an interactive bash
docker run -it -v /home/pi/:/data -v gfs:/gfs --net=spark --rm docker-spark bash
# copy files to glusterfs volume
cp /data/wordcount_data.txt /gfs/wordcount_data.txt

# run spark-submit
docker run -it -v /home/pi/:/data -v gfs:/gfs --net=spark --rm docker-spark spark-submit --master spark://sparkmaster:7077 /data/wordcount.py
```

