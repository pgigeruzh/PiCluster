# Installation of Hadoop on 1 Master and 2 Slaves
The first part is the configuration of Hadoop on the master (raspberrypi4 --> IP: 192.168.1.187)

//create new hadoop user
```bash
sudo addgroup hadoop  
sudo adduser --ingroup hadoop hduser  
sudo adduser hduser sudo  
```







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
