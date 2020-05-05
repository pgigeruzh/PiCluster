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

This is not a benchmark but a real-world dataset (https://grouplens.org/datasets/movielens/).

The benchmark used can be found at  `Movielens/ml-benchmark`, it runs 3 tests namely:
1. Finds the top rated movies containing a keyword, sorted by average rating, can set keyboard with --search="keyword"
2. Shows to top movies of a particular genre, can set genre with e.g --genre="Comedy"
3. Recommends movies to a specified user based on other users preferences e.g --user=2

The benchmarks tests manual defined map reduce, spark's sql library, and spark's ML libray. We also measure the time to load the database and the total runtime.
```bash
# download largest movielens dataset (190MB)
wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
unzip ml-20m.zip

# install numpy
sudo apt-get install python3-numpy -y

# Run, remember to set the correct file-path and spark master hostname
spark-submit --master spark://sparkmaster:7077  ml-benchmark.py ./ml-20m/movies.csv ./ml-20m/ratings.csv
```
Sample Result
```bash
# tables omitted for brevity
------------------------------
RESULTS
------------------------------
Load DB Time:           11.610222339630127
Map Reduce Time:        106.47479510307312
Sql Time:               65.75746655464172
Recommendation Time:    203.6552722454071
Total Runtime:          388.2532744407654
------------------------------
```
## Postgres

```bash
# Start pgbench inside a docker container
# (for GlusterFS, --mount source=gfs,destination=/var/lib/postgresql)
docker run --name pgbench -d --rm --network spark pgigeruzh/postgres
docker exec -it pgbench bash
sudo su - postgres

# Create an emty database on the test subject e.g. postgresmaster
# (-h: hostname)
createdb -h postgresmaster bench_test

# Initialize database with 1000000 rows (-s: scaling factor)
# (this creates 4 tables: pgbench_accounts, pgbench_branches, pgbench_history, pgbench_tellers)
pgbench -h postgresmaster -i -s 10 bench_test

# Run benchmark
# (-c: 8 clients, -j: 4 threads, -T: 1800 seconds, -P: print every 30s, -S: read-only)
pgbench -h postgresmaster -c 8 -j 4 -T 1800 -P 30 -S bench_test
# (-c: 80 clients, -j: 4 threads, -T: 1800 seconds, -P: print every 30s, -S: read-only)
pgbench -h postgresmaster -c 80 -j 4 -T 1800 -P 30 -S bench_test
```

## 