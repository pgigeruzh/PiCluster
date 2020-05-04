'''
Finds the top rated movies containing a keyword, sorted by average rating
Parameters e.g: program.py movies.csv ratings.csv --delim="," --search="star"

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

spark-submit --master spark://spark-master:7077  topmoviesearch.py u.item u.data
spark-submit --master spark://spark-master:7077  topmoviesearch.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topmoviesearch.py ./ml-10M100K/movies.dat ./10M100K/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topmoviesearch.py ./ml-20m/movies.csv ./ml-20m/ratings.csv --delim=","
'''
from pyspark.sql import SparkSession, Row
import pyspark.sql.functions as sf
import time
import argparse
from csv import reader
from itertools import islice

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default="|", help="The delimiter of the file: e.g --delimit=\"::\"")
parser.add_argument("--search", default='the', help="term to search for: --search=\"the\"")
args = parser.parse_args()

MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file
DELIMITER = args.delimit
SEARCH_TERM =  args.search
CONTAINS_HEADER = "false"


def check_header():
    global CONTAINS_HEADER
    with open(MOVIES_FILE, encoding='ascii', errors='ignore') as f:
        first_line = f.readline()
        fields = first_line.split(DELIMITER)
        CONTAINS_HEADER = "false" if fields[0].isnumeric() else "true"


def main():
    global DELIMITER
    check_header()

    spark = SparkSession.builder.appName("topmoviesearch").getOrCreate()
    if len(DELIMITER) == 1:
        movies_df = spark.read.load(MOVIES_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, inferSchema="true")
        if "u.data" in RATINGS_FILE:
            DELIMITER = '\t'
        rating_rdd = spark.read.load(RATINGS_FILE, format="csv", header=CONTAINS_HEADER, sep=DELIMITER, inferSchema="true").rdd
    else:
        rating_rdd = spark.read.option("header",CONTAINS_HEADER).text(RATINGS_FILE).rdd.map(lambda l: l[0].split(DELIMITER))
        movies_df = spark.read.option("header",CONTAINS_HEADER).text(MOVIES_FILE).rdd.map(lambda l: l[0].split(DELIMITER)).toDF()

    movies_df = movies_df.select(sf.col(movies_df.columns[0]).alias("movieId"), sf.col(movies_df.columns[1]).alias("title")) # ensures headers (df.schema.names) have right names

    movies_df.show(5)
    rating_rdd.toDF().show(5)

    rating_map = rating_rdd.map(lambda l: Row(int(l[1]), (float(l[2]), 1.0) ))                              # (movieID, (rating, 1.0))
    rating_reduce = rating_map.reduceByKey(lambda accum, item: ( accum[0] + item[0], accum[1] + item[1] ) ) # (movieID, (rating_sum, 1.0_sum))
    rating_reduce = rating_reduce.filter(lambda x : x[1][1] > 10)                                           # x = (a,(b,c)) c==x[1][1]
    rating_avg = rating_reduce.mapValues(lambda v : round(v[0] / v[1],2))                                   # rating_sum / 1.0_sum
    rating_df_sort = rating_avg.toDF().withColumnRenamed("_1","movieId").withColumnRenamed("_2","rating")
    rating_join_movie = rating_df_sort.join(movies_df, "movieId").orderBy("rating", ascending= False)
    rating_join_movie = rating_join_movie.filter(sf.lower((movies_df.title)).contains(SEARCH_TERM.lower()))

    rating_join_movie.show(10, False)
    print(f"> Top 10 movies containing keyword \"{SEARCH_TERM}\"")
    print("------------------------")

    spark.stop()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time() - start_time

    print("------------------------")
    print("Runtime: ", end_time)
    print("------------------------")