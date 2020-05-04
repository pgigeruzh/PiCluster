'''
Database:
sudo wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
sudo unzip ml-20m.zip

Run:
spark-submit --master spark://spark-master:7077  ml-benchmark.py ./ml-20m/movies.csv ./ml-20m/ratings.csv

Requires:
sudo apt-get install python3-numpy
[or] pip3 install scipy
if Python < 3.7 run: export PYTHONIOENCODING=UTF-8 

Tests:
1. Finds the top rated movies containing a keyword, sorted by average rating, can set keyboard with --search="keyword"
2. Shows to top movies of a particular genre, can set genre with e.g --genre="Comedy"
3. Recommends movies to a specified user based on other users preferences e.g --user=2
'''
from io import StringIO
import argparse
import time
import sys

from pyspark.sql import SparkSession, Row
import pyspark.sql.functions as sf
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, LongType, StringType

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default=",", help="The delimiter of the file: e.g --delimit=\"::\"")
parser.add_argument("--search", default='the', help="term to search for: --search=\"star\"")
parser.add_argument("--genre", default="Comedy", help="The desired genre: e.g --genre=\"Drama\"")
parser.add_argument("--user", default=1, type=int, help="The user id to recoment: e.g --user=1")
args = parser.parse_args()

MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
DELIMITER = args.delimit
SEARCH_TERM =  args.search
GENRE = args.genre
USER_ID = args.user
CONTAINS_HEADER = "false"

rating_schema = StructType([
    StructField("userId", IntegerType()),
    StructField("movieId", IntegerType()),
    StructField("rating", DoubleType()),
    StructField("timestamp", LongType()) ])

movie_schema = StructType([
    StructField("movieId", IntegerType()),
    StructField("title", StringType()),
    StructField("genres", StringType()) ])

def parse_ratings(line):
    fields = line.value.split(DELIMITER)
    return Row(userId = int(fields[0]), movieId = int(fields[1]), rating = float(fields[2]))

def parse_movies(line):
    fields = line.value.split(DELIMITER)
    return Row(movieId = int(fields[0]), title = str(fields[1]).encode('ascii', 'ignore').decode(),  genres = str(fields[2]).encode('ascii', 'ignore').decode() )


def check_header():
    global CONTAINS_HEADER
    with open(MOVIES_FILE, encoding='ascii', errors='ignore') as f:
        first_line = f.readline()
        fields = first_line.split(DELIMITER)
        CONTAINS_HEADER = "false" if fields[0].isnumeric() else "true"

def save_show_output(df):
    old_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout
    df.show(10, False)
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    return output

def load_dataframes(spark):
    if len(DELIMITER) == 1:
        movies_df = spark.read.load(MOVIES_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=movie_schema)
        rating_df = spark.read.load(RATINGS_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, schema=rating_schema)
    else:
        rating_df = spark.read.option("header",CONTAINS_HEADER).text(RATINGS_FILE).rdd.map(parse_ratings).toDF()
        movies_df = spark.read.option("header",CONTAINS_HEADER).text(MOVIES_FILE).rdd.map(parse_movies).toDF()
    return movies_df, rating_df

def test_search(spark,  movies_df, rating_df):
    rating_map = rating_df.rdd.map(lambda l: Row(int(l[1]), (float(l[2]), 1.0) ))                           # (movieID, (rating, 1.0))
    rating_reduce = rating_map.reduceByKey(lambda accum, item: ( accum[0] + item[0], accum[1] + item[1] ) ) # (movieID, (rating_sum, 1.0_sum))
    rating_reduce = rating_reduce.filter(lambda x : x[1][1] > 10)                                           # x = (a,(b,c)) c==x[1][1]
    rating_avg = rating_reduce.mapValues(lambda v : round(v[0] / v[1],2))                                   # rating_sum / 1.0_sum
    rating_df_sort = rating_avg.toDF().withColumnRenamed("_1","movieId").withColumnRenamed("_2","rating")
    rating_join_movie = rating_df_sort.join(movies_df, "movieId").orderBy("rating", ascending= False)
    rating_join_movie = rating_join_movie.filter(sf.lower((movies_df.title)).contains(SEARCH_TERM.lower()))

    pretty_table = save_show_output(rating_join_movie)
    return pretty_table


def test_genre(spark,  movies_df, rating_df):
    top_movies = rating_df.groupBy("movieID").count().filter("count > 500").join(rating_df.groupBy("movieID").avg("rating"), "movieID").join(movies_df, "movieID")
    top_movies_explode = top_movies.withColumn("genres", sf.explode(sf.split("genres", "[|]")))
    top_comedy = top_movies_explode.filter(f"genres == '{GENRE}'").orderBy("avg(rating)", ascending=False)
    result = top_comedy.select("title", "avg(rating)", "count")

    pretty_table = save_show_output(result)
    return pretty_table


def test_recommend(spark,  movies_df, rating_df):
    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating")
    model = als.fit(rating_df)

    ratings_list = rating_df.filter(f"userId='{USER_ID}'")
    user_ratings = ratings_list.join(movies_df,"movieId").select("title","rating").orderBy("rating", ascending= False)
    pretty_table1 = save_show_output(user_ratings)

    spark.conf.set("spark.sql.crossJoin.enabled", "true")
    ratingCounts = rating_df.groupBy("movieId").count().filter("count > 100")
    popularMovies = ratingCounts.select("movieId").withColumn('userId', sf.lit(USER_ID))
    recommendations = model.transform(popularMovies)
    user_recommendations = recommendations.join(movies_df,"movieId").select("title","prediction")
    user_recommendations = user_recommendations.sort(recommendations.prediction.desc())
    pretty_table2 = save_show_output(user_recommendations)

    return [pretty_table1, pretty_table2]



def main():
    timings = []

    start_time0 = time.time()
    spark = SparkSession.builder.appName("mlbenchmarks").getOrCreate()
    check_header()
    movies_df, rating_df = load_dataframes(spark)
    timings.append("Load DB Time:\t\t"+ str(time.time() - start_time0))

    start_time1 = time.time()
    res1 = test_search(spark,  movies_df, rating_df)
    timings.append("Map Reduce Time:\t"+ str(time.time() - start_time1))

    start_time2 = time.time()
    res2 = test_genre(spark,  movies_df, rating_df)
    timings.append("Sql Time:\t\t"+ str(time.time() - start_time2))

    start_time3 = time.time()
    res3 = test_recommend(spark,  movies_df, rating_df)
    timings.append("Recommendation Time:\t"+ str(time.time() - start_time3))

    spark.stop()
    print(f"> Top 10 movies containing keyword \"{SEARCH_TERM}\"")
    print(res1)
    print(f"> Top movies of genre: {GENRE}")
    print(res2)
    print(f"> Ratings of userId {USER_ID}:")
    print(res3[0])
    print(f"> Recommended Movies for userId {USER_ID}:")
    print(res3[1])

    return timings


if __name__ == "__main__":
    start_time = time.time()
    timings = main()
    timings.append("Total Runtime:\t\t"+ str(time.time() - start_time))

    print("------------------------------")
    print("RESULTS")
    print("------------------------------")
    for t in timings:
        print(t)
    print("------------------------------")

