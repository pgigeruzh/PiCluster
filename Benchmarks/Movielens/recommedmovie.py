'''
RUN: spark-submit --master spark://spark-master:7077  recommedmovie.py u.item u.data
RUN2: spark-submit --master spark://spark-master:7077 recommedmovie.py u.item u.data --test=2
'''
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from pyspark.sql.functions import lit
import argparse
import numpy
import time

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default="|", help="The delimiter of the file: e.g --delimit=\"::\"")
parser.add_argument("--test", default=1, type=int, help="Test 1: recommend user 0 movies, Test 2: Get the top 20 recommended movies")
args = parser.parse_args()

DELIMITER = args.delimit
MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
TEST_NO = args.test

def loadMovieNames():
    movies_path = MOVIES_FILE
    movieNames = {}
    with open(movies_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            fields = line.split(DELIMITER)
            movieNames[int(fields[0])] = fields[1]
    return movieNames


def parseInput(line):
    fields = line.value.split()
    return Row(userID = int(fields[0]), movieID = int(fields[1]), rating = float(fields[2]))

def test_1(ratings, movieNames):
    userRatings = ratings.filter("userID = 0")
    ratings_list = userRatings.collect()
    print("------------------------")
    print("Ratings for user ID 0:")
    for rating in ratings_list:
        print (movieNames[rating['movieID']], rating['rating'])
    print("------------------------")

def test_2(model, ratings, movieNames):
    ratingCounts = ratings.groupBy("movieID").count().filter("count > 100")
    popularMovies = ratingCounts.select("movieID").withColumn('userID', lit(0))
    recommendations = model.transform(popularMovies)
    topRecommendations = recommendations.sort(recommendations.prediction.desc()).take(20)
    print("------------------------")
    print("Top 20 Recommended Movies")
    for recommendation in topRecommendations:
        print (movieNames[recommendation['movieID']], recommendation['prediction'])
    print("------------------------")

if __name__ == "__main__":
    start_time = time.time()

    spark = SparkSession.builder.appName("RecommendMovies").getOrCreate()
    movieNames = loadMovieNames()
    lines = spark.read.text(RATINGS_FILE).rdd
    ratingsRDD = lines.map(parseInput)
    ratings = spark.createDataFrame(ratingsRDD).cache()
    als = ALS(maxIter=5, regParam=0.01, userCol="userID", itemCol="movieID", ratingCol="rating")
    model = als.fit(ratings)

    if TEST_NO == 2:
        spark.conf.set("spark.sql.crossJoin.enabled", "true")
        test_2(model, ratings, movieNames)
    else:
        test_1(ratings, movieNames)
    spark.stop()

    print("------------------------")
    print("Runtime: ", time.time() - start_time)
    print("------------------------")
