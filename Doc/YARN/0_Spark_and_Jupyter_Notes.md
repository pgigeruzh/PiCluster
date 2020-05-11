SPARK JOB

```bash
spark-submit --deploy-mode cluster --class org.apache.spark.examples.SparkPi $SPARK_HOME/examples/jars/spark-examples_2.11-2.4.5.jar 10
```

leave safemode in case of a full NameNode:
```bash
hdfs dfsadmin -safemode leave
```

if Namenode has no ressources:
```bash
hdfs fsck -delete
```

list all files in hdfs
```bash
hadoop fs -ls /
```

benchmark test

generate data
```bash
spark-submit --master yarn --deploy-mode cluster --name 'generate-benchmark-test-data' generate-data.py /opt/spark/examples/pyspark-benchmark/file -r 1000000 -p 1
```


shuffle benchmark on locally stored file
```bash
spark-submit --master yarn --deploy-mode cluster benchmark-shuffle.py /opt/spark/examples/pyspark-benchmark/file -r 1 -n 'shuffle-benchmark'
```

shuffle benchmark on locally stored file
```bash
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-shuffle.py /opt/spark/examples/pyspark-benchmark/file -r 1 -n 'shuffle-benchmark'
```

shuffle benchmark on HDFS
```bash
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-shuffle.py hdfs://192.168.1.187:9000/pyspark-benchmark/file
```

CPU benchmark test on HDFS

```bash
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-cpu.py hdfs://192.168.1.187:9000/pyspark-benchmark/file -s 40000000 -p 4 -n 'cpu-benchmark'
```


CPU benchmark test on locally stored file
```bash
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-cpu.py /opt/spark/examples/pyspark-benchmark/file -s 40000000 -p 4 -n 'cpu-benchmark'
```

Jupyter login 
```bash
ssh -L 8888:localhost:8888 hduser@192.168.1.187
click on localhost
```
