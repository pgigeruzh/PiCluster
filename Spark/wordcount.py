import sys
 
from pyspark.sql import SparkSession
 
if __name__ == "__main__":

    # create spark session
    spark = SparkSession\
        .builder\
        .appName("PythonPi")\
        .getOrCreate()

	# read data (spark-submit --files) and split each line into words
    words = spark.sparkContext.textFile("/gfs/wordcount_data.txt").flatMap(lambda line: line.split(" "))
	
	# count the occurrence of each word
    wordCounts = words.map(lambda word: (word, 1)).reduceByKey(lambda a,b:a +b)
	
	# save the counts to output
    wordCounts.saveAsTextFile("/gfs/wordcount_output/")

    # stop spark session
    spark.stop()