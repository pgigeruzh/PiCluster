# Installation Zookeeper

ssh to every single node
download zookeeper 

```bash
sudo wget https://downloads.apache.org/zookeeper/zookeeper-3.4.14/zookeeper-3.4.14.tar.gz

sudo tar zxvf zookeeper-3.4.14.tar.gz -C /opt/
sudo mv zookeeper-3.4.14 zookeeper
```
set environmental variable

```bash
sudo nano ~/.bashrc
add: export ZOO_HOME=/opt/zookeeper
source ~/.bashrc
```

edit configuration for zookeeper
```bash
cd $ZOO_HOME/conf
sudo nano zoo_sample.cfg

add:
# The number of milliseconds of each tick
tickTime=5000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=/tmp/zookeeper/data
# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the 
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
#autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
#autopurge.purgeInterval=1
initLimit=5
syncLimit=2
server.1=0.0.0.0:2888:3888
server.2=cluster3raspberry1:2888:3888
server.3=cluster3raspberry2:2888:3888
server.4=cluster3raspberry3:2888:3888
```

save as zoo.sample.cfg
Be aware that every localhost must be 0.0.0.0:2888:3888

create  directories

```bash
sudo mkdir -p /tmp/zookeeper/data
sudo chown hduser:hadoop /tmp/zookeeper/data/
chmod 750 /tmp/zookeeper/data/  

sudo mkdir -p /tmp/zookeeper
sudo chown hduser:hadoop /tmp/zookeeper
chmod 750 /tmp/zookeeper  
```

declare servers 
```bash
create myidfile for cluster config 
sudo nano /tmp/zookeeper/data/myid
add: 1
```
the second server needs to have myid declaration 2, the third 3 etc. 


start zookeeper
```bash
sudo $ZOO_HOME/bin/zkServer.sh start
```


# starting Quorom Node:

```bash
source /etc/environment

sudo chown hduser:hadoop /tmp/zookeeper/data/version-2/
chmod 750 /tmp/zookeeper/data/version-2/  

java -cp zookeeper-3.4.14.jar:lib/log4j-1.2.17.jar:lib/slf4j-log4j12-1.7.25.jar:lib/slf4j-api-1.7.25.jar:conf org.apache.zookeeper.server.quorum.QuorumPeerMain conf/zoo.cfg
```

start a server individually
```bash
bin/zkCli.sh -server cluster3raspberry2:2181
```


create & delete Node on Server to test
```bash
create /zk_znode_1 sample_data
ls /
get /zk_znode_1
delete /zk_znode_1
```
```bash

```
