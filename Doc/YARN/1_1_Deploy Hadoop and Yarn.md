# Installation of Hadoop on 1 Master and 2 Slaves
# Part 1: Installing Hadoop on MasterNode

(cluster3raspberry0 --> IP: 192.168.1.187)

Creating user "hduser" and creating ssh keys

```bash
#create new group and user "hduser"
sudo addgroup hadoop  
sudo adduser --ingroup hadoop hduser  
sudo adduser hduser sudo  

#login as hduser and create ssh keys 
su hduser
cd ~  
mkdir .ssh  
ssh-keygen -t rsa -P ""  
cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys 

```

Installation of Hadoop on the master node

```bash
#installing Hadoop
wget ftp://apache.belnet.be/mirrors/ftp.apache.org/hadoop/common/hadoop-2.7.1/hadoop-2.7.1.tar.gz  
sudo mkdir /opt  
cd ~  
sudo tar -xvzf hadoop-2.7.1.tar.gz -C /opt/  
cd /opt  
sudo chown -R hduser:hadoop hadoop-2.7.1/  

```
Set up some environmental variables on the master
```bash
#setting up environmental variables
nano ~/.bashrc
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:jre/bin/java::")
export HADOOP_HOME=/opt/hadoop-2.7.1
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

#apply .bashrc file
source ~/.bashrc  

#test hadoop installation
hadoop version

```
Configuring Hadoop on Master


```bash
# Go to configuration directory and set JAVA_HOME variable
cd $HADOOP_CONF_DIR  
nano hadoop-env.sh  

#put the following lines in this file:
# The java implementation to use:
export JAVA_HOME=/usr/lib/jvm/jdk-8-oracle-arm-vfp-hflt/jre/

```


```bash
# Stay in the same directory andput the XML-part into the core-site.xml file

nano core-site.xml

<configuration>
<property>
  <name>fs.default.name</name>
  <value>hdfs://cluster3raspberry0:9000</value>
</property>
<property>
  <name>hadoop.tmp.dir</name>
  <value>/hdfs/tmp</value>
</property>
</configuration>
```


```bash
# Stay in the same directory and put the XML-part into the hdfs-site.xml file

nano hdfs-site.xml

    <property>
            <name>dfs.replication</name>
            <value>4</value>
    </property>

```


```bash
# Create and edit mapred-site.xml

cp mapred-site.xml.template mapred-site.xml  
nano mapred-site.xml

<configuration>
<property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
  <property>
    <name>mapreduce.map.memory.mb</name>
    <value>1024</value>
  </property>
  <property>
    <name>mapreduce.map.java.opts</name>
    <value>-Xmx765m</value>
  </property> 
  <property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>2048</value>
  </property>
  <property>
    <name>mapreduce.reduce.java.opts</name>
    <value>-Xmx1530m</value>
  </property> 
  <property>
    <name>yarn.app.mapreduce.am.resource.mb</name>
    <value>1024</value>
  </property> 

</configuration>

```


```bash
# Stay in same directory and put the XML-part into yarn-site.xml

<configuration>
 <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>

  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>4</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>4096</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-mb</name>
    <value>128</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>2048</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-vcores</name>
    <value>1</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-vcores</name>
    <value>4</value>
  </property> 

<property>  
<name>yarn.resourcemanager.resource-tracker.address</name>  
<value>cluster3raspberry0:8025</value>  
</property>  
<property>  
<name>yarn.resourcemanager.scheduler.address</name>  
<value>cluster3raspberry0:8030</value>  
</property>  
<property>  
<name>yarn.resourcemanager.address</name>  
<value>cluster3raspberry0:8045</value>  
</property> 

</configuration>

 
```
Starting the Master

```bash
# Preparing and Booting HDFS
sudo mkdir -p /hdfs/tmp  
sudo chown hduser:hadoop /hdfs/tmp  
chmod 750 /hdfs/tmp  
hdfs namenode -format 

Create  file:/hdfs/tmp/dfs/data on master (since it should be also a worker)

sudo mkdir -p /hdfs/tmp/dfs/data
sudo chown hduser:hadoop /hdfs/tmp/
chmod 750 /hdfs/tmp/


#Booting HDFS
cd $HADOOP_HOME/sbin  
start-dfs.sh && start-yarn.sh  

```
To check if installation worked, enter jps
One should be able to see:
- NameNode
- DataNode
- NodeManager
- SecondaryNameNode
- RessourceManager #YARN
- JPS

# Part 2: Installing Hadoop on Slaves and connecting them to Master

This must be done on the master
```bash
# 
cd /etc
sudo nano hosts

#add the following lines (1 Master (also a slave) and 3 Slaves)
192.168.1.187  cluster3raspberry0
192.168.1.188  cluster3raspberry1
192.168.1.189  cluster3raspberry2
192.168.1.192  cluster3raspberry3

```
This must be done on the slaves: Java and openSSH-Server needs to be installed 


```bash
# create "hduser" on every slave
sudo addgroup hadoop  
sudo adduser --ingroup hadoop hduser  
sudo adduser hduser sudo  
```

```bash
#install openssh-server
 sudo apt-get -y install openssh-server 
```

On the MasterNode

```bash
#enable passwordless ssh from Master to Slaves 
su hduser  
ssh-keygen  
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys  
chmod 0600 ~/.ssh/authorized_keys  
ssh-copy-id hduser@cluster3raspberry1 #(!!!Repeat for each slave node!!!)  
ssh hduser@cluster3raspberry1

```

```bash
# Zip and transfer Haddop Files to Slaves (Repeat for each slave)
zip -r hadoop-2.7.1-with-armhf-drivers.zip /opt/hadoop-2.7.1/  

scp hadoop-2.7.1-with-armhf-drivers.zip hduser@raspberrypi5.local:~  
ssh hduser@raspberrypi5.local  
sudo unzip hadoop-2.7.1-with-armhf-drivers.zip -d /  
sudo chown -R hduser:hadoop /opt/hadoop-2.7.1/  
rm hadoop-2.7.1-with-armhf-drivers.zip  
exit  
scp ~/.bashrc hduser@cluster3raspberry1.local:~/.bashrc  
 
```

```bash
# Wipe HDFS
rm -rf /hdfs/tmp/*  
 
```
On every single node:
```bash
# add this xml property in every yarn-site.xml file between the configurations tags
sudo nano yarn-site.xml

<configuration>
 <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>4</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>4096</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-mb</name>
    <value>128</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>2048</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-vcores</name>
    <value>1</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-vcores</name>
    <value>4</value>
  </property>
  <property>
    <name>yarn.nodemanager.vmem-check-enabled</name>
    <value>false</value>
  </property>

<property>
<name>yarn.resourcemanager.resource-tracker.address</name>
<value>cluster3raspberry0:8025</value>
</property>
<property>
<name>yarn.resourcemanager.scheduler.address</name>
<value>cluster3raspberry0:8030</value>
</property>
<property>
<name>yarn.resourcemanager.address</name>
<value>cluster3raspberry0:8040</value>
</property>


</configuration>

```

```bash
<configuration>
<property>  
  <name>fs.default.name</name>
  <value>hdfs://cluster3raspberry0:9000</value>
</property>  
<property>  
  <name>hadoop.tmp.dir</name>
  <value>/hdfs/tmp</value>
</property> 
</configuration>


```
On the masternode
```bash
# edit the slaves file and add the following
sudo nano slaves

cluster3raspberry0
cluster3raspberry1
cluster3raspberry2
cluster3raspberry3
```
Create  file:/hdfs/tmp/dfs/data on every slave and give permission

```bash
sudo mkdir -p /hdfs/tmp/dfs/data
sudo chown hduser:hadoop /hdfs/tmp/
chmod 750 /hdfs/tmp/

```

Start the master and the slaves on the master:

```bash
# starting
start-dfs.sh && start-yarn.sh

# stoping
stop-dfs.sh && stop-yarn.sh

```
To check if installation worked on the Master, enter jps on the MasterNode
One should be able to see:
- NameNode
- NodeManager
- SecondaryNameNode
- RessourceManager #YARN
- Datanode (if also configured on the master) 
- JPS

To check if installation worked on the Slaves, enter jps on Slaves
One should be able to see:
- DataNode
- NodeManager #YARN
- JPS
