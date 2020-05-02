'''
Requires: 
sudo apt-get install python-numpy
[or] pip3 install scipy

Databases:
sudo wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
sudo wget http://files.grouplens.org/datasets/movielens/ml-10m.zip
sudo wget http://files.grouplens.org/datasets/movielens/ml-20m.zip

sudo unzip ml-1m.zip
sudo unzip ml-10m.zip
sudo unzip ml-20m.zip

Run:
program <movies_file> <ratings_file> <tag>

Tags:
--delim: the delimitor/seperator of the file e.g --delim=","
--header: specify if the file has headers e.g --deader="true"

spark-submit --master spark://spark-master:7077  recommedmovie.py u.item u.data
spark-submit --master spark://spark-master:7077  recommedmovie.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  recommedmovie.py ./ml-10M100K/movies.dat ./10M100K/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  recommedmovie.py ./ml-20m/movies.csv ./ml-20m/ratings.csv --delim="," --header="true"
'''
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from pyspark.sql.functions import lit
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType

from csv import reader
import argparse
import numpy
import time

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default="|", help="The delimiter of the file: e.g --delimit=\"::\"")
parser.add_argument("--header", default="false", help="If file contains header: --header=\"true\"")
args = parser.parse_args()

DELIMITER = args.delimit
MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
CONTAINS_HEADER = args.header

rating_schema = StructType([
    StructField("userID", IntegerType()),
    StructField("movieID", IntegerType()),
    StructField("rating", DoubleType()),
    StructField("timestamp", IntegerType())])


def loadMovieNames():
    movies_path = MOVIES_FILE
    movieNames = {}
    with open(movies_path, encoding='utf-8', errors='replace') as f:
        if CONTAINS_HEADER == "true":
            f.readline()
        if len(DELIMITER) != 1:
            for line in f:
                fields = line.split(DELIMITER)
                movieNames[int(fields[0])] =  str(fields[1]).encode('ascii', 'ignore').decode()
        else:
            csv_reader = reader(f, delimiter=DELIMITER)
            for line in csv_reader:
                movieNames[int(line[0])] = str(line[1]).encode('ascii', 'ignore').decode()
    return movieNames


def parseInput(line):
    if "u.data" in RATINGS_FILE: # special case: u.data uses tabs
        fields = line.value.split('\t')
    else:
        fields = line.value.split(DELIMITER)
    return Row(userID = int(fields[0]), movieID = int(fields[1]), rating = float(fields[2]))


def get_ratings(ratings, movieNames, userID = 1, take_num = 10):
    userRatings = ratings.filter(f"userID={userID}")
    ratings_list = userRatings.take(take_num)
    return ratings_list


def get_recommendations(model, ratings, movieNames, userID = 1, take_num = 10):
    ratingCounts = ratings.groupBy("movieID").count().filter("count > 100")
    popularMovies = ratingCounts.select("movieID").withColumn('userID', lit(userID))
    recommendations = model.transform(popularMovies)
    recommendations_sorted = recommendations.sort(recommendations.prediction.desc()).take(take_num)
    return recommendations_sorted

if __name__ == "__main__":
    start_time = time.time()

    spark = SparkSession.builder.appName("RecommendMovies").getOrCreate()
    movieNames = loadMovieNames()
    if CONTAINS_HEADER == "true":
        df = spark.read.load(RATINGS_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=rating_schema).rdd
    else: # older movielens db use double char delimiters :: not supported by spark
        df = spark.read.text(RATINGS_FILE).rdd
        df = df.map(parseInput)

    ratings = spark.createDataFrame(df).cache()
    als = ALS(maxIter=5, regParam=0.01, userCol="userID", itemCol="movieID", ratingCol="rating")
    model = als.fit(ratings)

    user_ratings = get_ratings(ratings, movieNames)
    spark.conf.set("spark.sql.crossJoin.enabled", "true")
    user_recommendations = get_recommendations(model, ratings, movieNames)
    spark.stop()
    runtime = time.time() - start_time

    print("------------------------")
    print("Runtime: ", runtime)
    print("------------------------")


    print("------------------------")
    print("> Ratings for userID 1:")
    for rating in user_ratings:
        print (movieNames[int(rating['movieID'])], rating['rating'])
    print("------------------------")


    print("------------------------")
    print("> Recommended Movies for userID 1:")
    for recommendation in user_recommendations:
        print (movieNames[int(recommendation['movieID'])], recommendation['prediction'])
    print("------------------------")


    print("------------------------")
    print("Runtime: ", runtime)
    print("------------------------")
