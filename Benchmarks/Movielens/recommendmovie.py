'''
Recommends movies to a specified user based on other users preferences
Parameters e.g: program.py movies.csv ratings.csv --delim="," --user=2

Requires:
sudo apt-get install python3-numpy
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
--delim=","  the delimitor/seperator of the file set to e.g a comma
--used=2     the user id to recommend set to e.g id 2

spark-submit --master spark://spark-master:7077  recommendmovie.py u.item u.data
spark-submit --master spark://spark-master:7077  recommendmovie.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  recommendmovie.py ./ml-10M100K/movies.dat ./10M100K/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  recommendmovie.py ./ml-20m/movies.csv ./ml-20m/ratings.csv --delim=","
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
parser.add_argument("--user", default=1, type=int, help="The user id to recoment: e.g --user=1")
args = parser.parse_args()

DELIMITER = args.delimit
MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
USER_ID = args.user
CONTAINS_HEADER = "false"

rating_schema = StructType([
    StructField("userId", IntegerType()),
    StructField("movieId", IntegerType()),
    StructField("rating", DoubleType()),
    StructField("timestamp", IntegerType())])

def check_header():
    global CONTAINS_HEADER
    with open(MOVIES_FILE, encoding='ascii', errors='ignore') as f:
        first_line = f.readline()
        fields = first_line.split(DELIMITER)
        CONTAINS_HEADER = "false" if fields[0].isnumeric() else "true"

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
    return Row(userId = int(fields[0]), movieId = int(fields[1]), rating = float(fields[2]))


def get_ratings(ratings, movieNames, take_num = 10):
    userRatings = ratings.filter(f"userId='{USER_ID}'")
    ratings_list = userRatings.take(take_num)
    return ratings_list


def get_recommendations(model, ratings, movieNames, take_num = 10):
    ratingCounts = ratings.groupBy("movieId").count().filter("count > 100")
    popularMovies = ratingCounts.select("movieId").withColumn('userId', lit(USER_ID))
    recommendations = model.transform(popularMovies)
    recommendations_sorted = recommendations.sort(recommendations.prediction.desc()).take(take_num)
    return recommendations_sorted

def main():
    spark = SparkSession.builder.appName("RecommendMovies").getOrCreate()
    check_header()
    movieNames = loadMovieNames()
    if CONTAINS_HEADER == "true":
        rating_df = spark.read.load(RATINGS_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=rating_schema).rdd
    else: # older movielens db use double char delimiters :: not supported by spark
        rating_df = spark.read.text(RATINGS_FILE).rdd.map(parseInput)

    ratings = spark.createDataFrame(rating_df).cache()
    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating")
    model = als.fit(ratings)

    user_ratings = get_ratings(ratings, movieNames)
    spark.conf.set("spark.sql.crossJoin.enabled", "true")
    user_recommendations = get_recommendations(model, ratings, movieNames)
    spark.stop()

    print("------------------------------------------------")
    print(f"> Ratings of userId {USER_ID}:")
    for rating in user_ratings:
        movie_name = movieNames[int(rating['movieId'])]
        rating_value = rating['rating']
        print("{:<50} {:<}".format(movie_name[:40],rating_value))
    print("------------------------------------------------")

    print("------------------------------------------------")
    print(f"> Recommended Movies for userId {USER_ID}:")
    for recommendation in user_recommendations:
        movie_name = movieNames[int(recommendation['movieId'])]
        rating_value = round(float(recommendation['prediction']),2)
        print("{:<50} {:<}".format(movie_name[:40],rating_value))
    print("------------------------------------------------")


if __name__ == "__main__":
    start_time = time.time()
    main()
    runtime = time.time() - start_time

    print("------------------------------------------------")
    print("Runtime: ", runtime)
    print("------------------------------------------------")
