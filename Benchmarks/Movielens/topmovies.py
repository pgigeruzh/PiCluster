'''
sudo wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
sudo unzip ml-1m.zip
RUN: spark-submit --master spark://spark-master:7077 topmovies.py ./ml-1m/movies.dat ./ml-1m/ratings.dat --delimit="::"

sudo wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
sudo unzip ml-20m.zip
RUN: spark-submit --master spark://spark-master:7077 topmovies.py ./ml-20m/movies.csv ./ml-20m/ratings.csv

'''
from pyspark import SparkConf, SparkContext
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("movies_file", help="Movies File")
parser.add_argument("ratings_file", help="Ratings File")
parser.add_argument("--delimit", default=",", help="The delimiter of the file: e.g --delimit=\"::\"")
args = parser.parse_args()

DELIMITER = args.delimit
MOVIES_FILE = args.movies_file
RATINGS_FILE = args.ratings_file


def loadMovieNames():
    movies_path = MOVIES_FILE
    movieNames = {}
    with open(movies_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            fields = line.split(DELIMITER)
            if(fields[0].isdigit()):
                movieNames[int(fields[0])] = fields[1]
    return movieNames

# Take each line of u.data and convert it to (movieID, (rating, 1.0))
def parseInput(line):
   fields = line.split(DELIMITER)
   if(fields[1].isdigit() and fields[2].replace(".", "", 1).isdigit()):
       return (int(fields[1]), (float(fields[2]), 1.0))
   return (0, (0.0, 1.0))

if __name__ == "__main__":
    start_time = time.time()
    conf = SparkConf().setAppName("TopMovies")
    sc = SparkContext(conf = conf)

    movieNames = loadMovieNames()
    userdata_path = RATINGS_FILE
    lines = sc.textFile(userdata_path)
    movieRatings = lines.map(parseInput)

    # Reduce to (movieID, (sumOfRatings, totalRatings))
    ratingTotalsAndCount = movieRatings.reduceByKey(lambda movie1, movie2: ( movie1[0] + movie2[0], movie1[1] + movie2[1] ) )

    # Map to (rating, averageRating) the Sort by average rating
    averageRatings = ratingTotalsAndCount.mapValues(lambda totalAndCount : totalAndCount[0] / totalAndCount[1])
    sortedMovies = averageRatings.sortBy(lambda x: x[1], ascending= False)

    results = sortedMovies.take(5)
    for result in results:
        movie_name = movieNames[result[0]].encode('ascii', 'ignore').decode('ascii')
        print(movie_name, result[1])
    time_elapsed = time.time() - start_time
    print("Runtime: ", time_elapsed)
