'''
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

spark-submit --master spark://spark-master:7077  topmovies.py u.item u.data
spark-submit --master spark://spark-master:7077  topmovies.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topmovies.py ./ml-10M100K/movies.dat ./10M100K/ratings.dat --delim="::"
spark-submit --master spark://spark-master:7077  topmovies.py ./ml-20m/movies.csv ./ml-20m/ratings.csv --delim="," --header="true"
'''
from pyspark import SparkConf, SparkContext
import time
import argparse
from csv import reader
from itertools import islice

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

# Take each line of u.data and convert it to (movieID, (rating, 1.0))
def parseInput(line):
    if "u.data" in RATINGS_FILE: # special case: u.data uses tabs
        fields = line.split('\t')
    else:
        fields = line.split(DELIMITER)
    if fields[1].isdigit():
        return (int(fields[1]), (float(fields[2]), 1.0))
    return None

if __name__ == "__main__":
    start_time = time.time()
    conf = SparkConf().setAppName("TopMovies")
    sc = SparkContext(conf = conf)

    movieNames = loadMovieNames()
    lines = sc.textFile(RATINGS_FILE)
    if CONTAINS_HEADER == "true":
        lines = lines.mapPartitionsWithIndex(lambda idx, it: islice(it, 1, None) if idx == 0 else it )
    movieRatings = lines.map(parseInput)

    # Reduce to (movieID, (sumOfRatings, totalRatings))
    ratingTotalsAndCount = movieRatings.reduceByKey(lambda movie1, movie2: ( movie1[0] + movie2[0], movie1[1] + movie2[1] ) )

    # Map to (rating, averageRating) the Sort by average rating
    averageRatings = ratingTotalsAndCount.mapValues(lambda totalAndCount : totalAndCount[0] / totalAndCount[1])
    sortedMovies = averageRatings.sortBy(lambda x: x[1], ascending= False)

    results = sortedMovies.take(5)
    
    print("------------------------")
    print("> Top 5 movies:")
    for result in results:
        print( movieNames[result[0]], result[1])
    print("------------------------")

    print("------------------------")
    print("Runtime: ", time.time() - start_time)
    print("------------------------")