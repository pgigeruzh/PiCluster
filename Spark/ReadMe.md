# Spark

This folder contains examples to run on Spark. The recommended way is to use spark-submit. For example, running the pi.py file on Spark works as follows:

```bash
# spark-submit pi.py
spark-submit --master spark://sparkmaster:7077 /data/pi.py
```

Alternatively, it is possible to define the Spark master in the file itself. For example, the pi.py file would look something like this:

```python
from __future__ import print_function

import sys
from random import random
from operator import add

from pyspark.sql import SparkSession


if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .master("spark://sparkmaster:7077")\ # define the master here
        .appName("PythonPi")\
        .getOrCreate()

    partitions = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    n = 100000 * partitions

    def f(_):
        x = random() * 2 - 1
        y = random() * 2 - 1
        return 1 if x ** 2 + y ** 2 <= 1 else 0

    count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
    print("Pi is roughly %f" % (4.0 * count / n))

    spark.stop()
```