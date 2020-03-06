# Installation of Hadoop on 1 Master and 2 Slaves

(raspberrypi4 --> IP: 192.168.1.187)

Creating user "hduser" and creating ssh keys

```bash
#create new group and user "hduser"
sudo addgroup hadoop  
sudo adduser --ingroup hadoop hduser  
sudo adduser hduser sudo  
```

```bash
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
# Stay in the same directory and edit the core-site.xml file

<property>
  <name>fs.default.name</name>
  <value>hdfs://raspberrypi4:54310</value>
</property>
<property>
  <name>hadoop.tmp.dir</name>
  <value>/hdfs/tmp</value>
</property>

```



```bash
# Stay in the same directory and edit the hdfs-site.xml file
<property>
    <name>dfs.replication</name>
    <value>1</value>
</property>

 
```


```bash
# Create and edit mapred-site.xml

cp mapred-site.xml.template mapred-site.xml  
nano mapred-site.xml

  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
  <property>
    <name>mapreduce.map.memory.mb</name>
    <value>2500</value>
  </property>
  <property>
    <name>mapreduce.map.java.opts</name>
    <value>-Xmx210m</value>
  </property>
  <property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>2500</value>
  </property>
  <property>
    <name>mapreduce.reduce.java.opts</name>
    <value>-Xmx210m</value>
  </property>
  <property>
    <name>yarn.app.mapreduce.am.resource.mb</name>
    <value>2500</value>
  </property>

```


```bash
# Stay in same directory and edit yarn-site.xml

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
    <value>3072</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-mb</name>
    <value>64</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>3072</value>
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
<value>raspberrypi4:8025</value>  
</property>  
<property>  
<name>yarn.resourcemanager.scheduler.address</name>  
<value>raspberrypi4:8030</value>  
</property>  
<property>  
<name>yarn.resourcemanager.address</name>  
<value>raspberrypi4:8040</value>  
</property> 
 
```

```bash
# Preparing and Booting HDFS
sudo mkdir -p /hdfs/tmp  
sudo chown hduser:hadoop /hdfs/tmp  
chmod 750 /hdfs/tmp  
hdfs namenode -format 

#Booting HDFS
cd $HADOOP_HOME/sbin  
start-dfs.sh && start-yarn.sh  

```
To check if installation worked, enter jps
One should be able to see:
- NameNode
- SecondaryNameNode
- RessourceManager //YARN
- Datanode (if configured)
- JPS



```bash
#
 
```


```bash
#
 
```


```bash
#
 
```

