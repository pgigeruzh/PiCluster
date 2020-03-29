# Benchmarks

This section contains information about different benchmarks for Spark.



## PySpark-Benchmark

PySpark-Benchmark (https://github.com/DIYBigData/pyspark-benchmark) is a lightweight, easy to use benchmarking utility for PySpark. Most other benchmarks are made in Scala, hence, not representative for this project (Python). To run this benchmark, clone the repo and spark-submit the files.

```bash
# clone repo
git clone https://github.com/DIYBigData/pyspark-benchmark.git

# generate file to /gfs/file (71M)
spark-submit --master spark://sparkmaster:7077 --name 'generate-benchmark-test-data' generate-data.py /gfs/file -r 1000000 -p 1
# or download a pre-generated file from dropbox
wget -O file.zip https://www.dropbox.com/s/qjgdoj9p9tvdspa/file.zip?dl=1
unzip file.zip

# run shuffle benchmark
spark-submit --master spark://sparkmaster:7077 benchmark-shuffle.py /gfs/file -r 1 -n 'shuffle-benchmark'

# run CPU benchmark
spark-submit --master spark://sparkmaster:7077 benchmark-cpu.py /gfs/file -s 40000000 -p 4 -n 'cpu-benchmark'
```
For Yarn-Cluster

```bash
#download a pre-generated file from dropbox
wget -O file.zip https://www.dropbox.com/s/qjgdoj9p9tvdspa/file.zip?dl=1
unzip file.zip

#copy to hdfs
hdfs dfs -copyFromLocal /opt/spark/examples/pyspark-benchmark /pyspark-benchmark

# run shuffle benchmark
spark-submit --master yarn --deploy-mode cluster --num-executors 14 benchmark-shuffle.py hdfs://192.168.1.187:9000/pyspark-benchmark/file

# run CPU benchmark
spark-submit --master yarn --deploy-mode cluster --num-executors 14 --executor-cores 1 benchmark-cpu.py hdfs://192.168.1.187:9000/pyspark-benchmark/file -s 40000000 -p 4 -n 'cpu-benchmark'
```

## Movielens

This is not a benchmark but a real-world dataset (https://grouplens.org/datasets/movielens/). An example project that uses the movielens dataset can be found in "Movielens/draft.py". The file is originally from: https://gist.github.com/jianyu0503/4753344051572c8fc7aa18123eafd2cc

```bash
# download largest movielens dataset (190MB)
wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
unzip ml-20m.zip

# spark-submit movielens.py (takes around 5 minutes to finish)
# don't forget to change the file paths!
spark-submit --master spark://sparkmaster:7077 --packages com.databricks:spark-csv_2.11:1.5.0 movielens.py
```

For Yarn-Cluster
```bash
hdfs dfs -copyFromLocal /opt/spark/examples/ml-20m /ml-20m
hdfs dfsadmin -safemode leave
spark-submit --master yarn --deploy-mode cluster --num-executors 14 --packages com.databricks:spark-csv_2.11:1.5.0 movielens.py hdfs://192.168.1.187:9000/ml-20m
```
Output Yarn
```bash
+------+----+
|   tag| cnt|
+------+----+
|sci-fi|3384|
+------+----+

+------+-------+
|genres|    cnt|
+------+-------+
| Drama|1467402|
+------+-------+

Duration: 4min 32 sec
```

## Spark-Bench

Spark-Bench (https://github.com/CODAIT/spark-bench) is not suitable because the data (hundreds of gigabytes) is not scalable.
