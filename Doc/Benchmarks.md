# Benchmarks

This section contains information about different benchmarks for Spark.



## PySpark-Benchmark

PySpark-Benchmark (https://github.com/DIYBigData/pyspark-benchmark) is a lightweight, easy to use benchmarking utility for PySpark. Most other benchmarks are made in Scala, hence, not representative for this project (Python). To run this benchmark, clone the repo and spark-submit the files.

```
# clone repo
git clone https://github.com/DIYBigData/pyspark-benchmark.git

# generate file to /gfs/file (71M)
spark-submit --master spark://sparkmaster:7077 --name 'generate-benchmark-test-data' generate-data.py /gfs/file -r 1000000 -p 1
	
# run shuffle benchmark
spark-submit --master spark://sparkmaster:7077 benchmark-shuffle.py /gfs/file -r 1 -n 'shuffle-benchmark'

# run CPU benchmark
spark-submit --master spark://sparkmaster:7077 benchmark-cpu.py /gfs/file -s 80000000 -p 4 -n 'cpu-benchmark'
```



## Spark-Bench

Spark-Bench (https://github.com/CODAIT/spark-bench) is not suitable because the data (hundreds of gigabytes) is not scalable.