# Installation of Hadoop on 1 Master and 2 Slaves
The first part is the installation & configuration of Hadoop on the master node
(raspberrypi4 --> IP: 192.168.1.187)


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

```bash
#installing Hadoop
wget ftp://apache.belnet.be/mirrors/ftp.apache.org/hadoop/common/hadoop-2.7.1/hadoop-2.7.1.tar.gz  
sudo mkdir /opt  
cd ~  
sudo tar -xvzf hadoop-2.7.1.tar.gz -C /opt/  
cd /opt  
sudo chown -R hduser:hadoop hadoop-2.7.1/  

```

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



