SPARK JOB
spark-submit --deploy-mode cluster --class org.apache.spark.examples.SparkPi $SPARK_HOME/examples/jars/spark-examples_2.11-2.4.5.jar 10

#leave safemode:
hdfs dfsadmin -safemode leave

#if Namenode has no ressources:
hdfs fsck -delete

#list all files in hdfs
hadoop fs -ls -R


#INFO FOR SPARK
$HADOOP_CONF_DIR --> core-site.xml port must be set to 9000

#benchmark test

#generate data
spark-submit --master yarn --deploy-mode cluster --name 'generate-benchmark-test-data' generate-data.py /opt/spark/examples/pyspark-benchmark/file -r 1000000 -p 1

#shuffle benchmark on locally stored file
spark-submit --master yarn --deploy-mode cluster benchmark-shuffle.py /opt/spark/examples/pyspark-benchmark/file -r 1 -n 'shuffle-benchmark'

#shuffle benchmark on locally stored file
spark-submit --master yarn --deploy-mode cluster --num-executors 14 --executor-cores 1 benchmark-shuffle.py /opt/spark/examples/pyspark-benchmark/file -r 1 -n 'shuffle-benchmark'

#shuffle benchmark on HDFS
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-shuffle.py hdfs://192.168.1.187:9000/pyspark-benchmark/file



#CPU benchmark test on HDFS
spark-submit --master yarn --deploy-mode cluster --num-executors 14 --executor-cores 1 benchmark-cpu.py hdfs://192.168.1.187:9000/pyspark-benchmark/file -s 40000000 -p 4 -n 'cpu-benchmark'

#CPU benchmark test on locally stored file
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-cpu.py /opt/spark/examples/pyspark-benchmark/file -s 40000000 -p 4 -n 'cpu-benchmark'

#INFO error message 80 Mio. Samples
20/03/23 17:27:36 WARN scheduler.TaskSetManager: Stage 1 contains a task of very large size (97915 KB). The maximum recommended task size is 100 KB.
20/03/23 17:27:36 INFO scheduler.TaskSetManager: Starting task 0.0 in stage 1.0 (TID 4, cluster3raspberry1, executor 9, partition 0, PROCESS_LOCAL, 100265853 bytes)
20/03/23 17:27:37 INFO scheduler.TaskSetManager: Starting task 1.0 in stage 1.0 (TID 5, cluster3raspberry3, executor 10, partition 1, PROCESS_LOCAL, 100397181 bytes)
Exception in thread "dispatcher-event-loop-3" java.lang.OutOfMemoryError: Java heap space


#jupyter login 
ssh -L 8888:localhost:8888 hduser@192.168.1.187
click on localhost







