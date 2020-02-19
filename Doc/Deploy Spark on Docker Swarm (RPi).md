# Deploy Spark on Docker Swarm (RPi)

To deploy spark on docker swarm, you first need to have a "Spark" docker image. The few options available are for x86 and not arm, therefore, you need to either 1) create your own or 2) build/compile an existing one yourself. We have decided to go with the latter one. It needs to be noted that, at the time of writing this article, Raspian is still 32 bit and can therefore not run arm64 images.

First, connect to your swarm master. Then, clone this git repo: www.github.com/Gradiant/dockerized-spark.git. It contains a Dockerfile for running Spark and works on arm too. Then, build the docker image and name it "dockerized-spark". 

(Caution: The image needs to be built on every raspberry in the cluster! Otherwise, the error "No such image" occurs.)

```bash
# connect to swarm master
ssh pi@192.168.2.205

# clone repo
git clone https://github.com/Gradiant/dockerized-spark.git
cd dockerized-spark

# build image
docker build -t dockerized-spark -f alpine/Dockerfile .
# check available docker images
docker images
```

Before deploying it on Swarm, you can try it locally using:

```bash
# run spark master
docker run -d -p 8080:8080 -p 7077:7077 --name sparkmaster dockerized-spark standalone master
# run spark workers
# change the ip to whatever the spark master got (docker inspect sparkmaster)
docker run -d --name sparkworker1 dockerized-spark standalone worker spark://172.17.0.2:7077
docker run -d --name sparkworker2 dockerized-spark standalone worker spark://172.17.0.2:7077
```

To deploy it on a Swarm, you need to:

```bash
# label nodes to be able to distribute work manually
docker node update --label-add type=sparkmaster raspberrypi0
docker node update --label-add type=sparkworker raspberrypi1

# create an attachable overlay network
docker network create -d overlay --attachable spark

# run spark master
docker service create --publish 8080:8080 --publish 7077:7077 --network spark --constraint node.labels.type==sparkmaster --name sparkmaster dockerized-spark standalone master
# run spark workers
docker service create --replicas 2 --network spark --publish 8081:8081 --constraint node.labels.type==sparkworker --name sparkworker dockerized-spark standalone worker spark://sparkmaster:7077
```

To see if it worked, visit the ip of your Swarm master e.g.192.168.2.205:8080
Furthermore, you can run:

```bash
# visualizer on port 80
docker service create --name=viz --publish=80:8080/tcp --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock alexellis2/visualizer-arm:latest

# command line
docker service ls

# connect the Spark Client with "spark-submit"
# (you need to be in the overlay networktherefore it won't work from outside the cluster)
docker run -ti --net spark --rm dockerized-spark spark-submit --master spark://sparkmaster:7077 --class org.apache.spark.examples.SparkPi $SPARK_HOME/examples/jars/spark-examples_2.11-2.4.0.jar 100

# for debugging purposes, a standard webserver might be useful as well
# it should be available on every node on port 81
docker service create --name nginx --replicas 2 --publish published=81,target=80 nginx
```

