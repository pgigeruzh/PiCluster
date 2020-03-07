# Mapreduce examples

Be sure that $HADOOP_CONF_DIR/conf-site.xml is configured on Port 54310

```bash
# sudo nano conf-site
<configuration>
<property>
  <name>fs.default.name</name>
  <value>hdfs://raspberrypi4:54310</value>
</property>
<property>
  <name>hadoop.tmp.dir</name>
  <value>/hdfs/tmp</value>
</property>
</configuration>

```
1. Example: Use license.txt file to do a wordcount example

```bash
# Upload file to hdfs
hadoop dfs -copyFromLocal /opt/hadoop-2.7.1/LICENSE.txt /license.txt

```

```bash
# Run wordcount example
hadoop jar /opt/hadoop-2.7.1/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.1.jar wordcount /license.txt /license-out.txt

```

```bash
# copy output file to local filesystem
hadoop dfs -copyToLocal /license-out.txt ~/
```




