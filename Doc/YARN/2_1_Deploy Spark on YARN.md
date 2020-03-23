# Spark 2.4.5 installation on Hadoop 2.7.1
# Part 3: Installing Spark on Cluster

The installation only needs to be done on the MasterNode (Raspberrypi4)
```bash
# download and unzip Spark installation files
cd /opt/hadoop-2.7.1
wget https://downloads.apache.org/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvf spark-2.4.5-bin-hadoop2.7.tgz
mv spark-2.4.5-bin-hadoop2.7.tgz spark
```


```bash
# set additional environmental variables to integrate Spark with Yarn
nano ~/.bashrc 

export SPARK_HOME=/opt/spark-3.0.0-preview2-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin
export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native:$LD_LIBRARY_PATH

source ~/.bashrc  
```


```bash
# edit Spark config file
mv $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf

#in spark-defaults.conf, set yarn as spark-master and limit some ressources

spark.master                     yarn
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://cluster3raspberry0:9000/spark-logs
#spark.eventLog.dir              hdfs://raspberrypi4:8021/directory

# spark.serializer                 org.apache.spark.serializer.KryoSerializer
#spark.driver.memory              512m
# spark.executor.extraJavaOptions  -XX:+PrintGCDetails -Dkey=value -Dnumbers="one two three"
#spark.yarn.am.memory		 465m
spark.executor.memory            640m
spark.history.provider           org.apache.spark.deploy.history.FsHistoryProvider
spark.history.fs.logDirectory    hdfs://cluster3raspberry0:9000/spark-logs
spark.history.fs.update.interval 10s
spark.history.ui.port            18080

spark.driver.memoryOverhead	 1024
# spark.executor.memoryOverhead	 512


```
If there's a SPARK request, which needs more memory than allowed, YARN wil reject creation of a container
Thus I have set some ressource limitations (above). Must be also done for YARN. 
```bash
# check the settings in the yarn-site.xml file 

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

```

```bash
# 

```
