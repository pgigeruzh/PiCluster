'''
RUN: spark-submit --master spark://spark-master:7077 topmovies.py u.item u.data
'''
from pyspark import SparkConf, SparkContext
import sys
import time

def loadMovieNames():
    movies_path = sys.argv[1] #u.item
    movieNames = {}
    with open(movies_path, encoding='latin-1') as f:
        for line in f:
            fields = line.split('|')
            movieNames[int(fields[0])] = fields[1]
    return movieNames

# Take each line of u.data and convert it to (movieID, (rating, 1.0))
def parseInput(line):
   fields = line.split()
   return (int(fields[1]), (float(fields[2]), 1.0))

if __name__ == "__main__":
    start_time = time.time()
    conf = SparkConf().setAppName("TopMovies")
    sc = SparkContext(conf = conf)

    movieNames = loadMovieNames()
    userdata_path = sys.argv[2] #u.data
    lines = sc.textFile(userdata_path)
    movieRatings = lines.map(parseInput)

    # Reduce to (movieID, (sumOfRatings, totalRatings))
    ratingTotalsAndCount = movieRatings.reduceByKey(lambda movie1, movie2: ( movie1[0] + movie2[0], movie1[1] + movie2[1] ) )

    # Map to (rating, averageRating) the Sort by average rating
    averageRatings = ratingTotalsAndCount.mapValues(lambda totalAndCount : totalAndCount[0] / totalAndCount[1])
    sortedMovies = averageRatings.sortBy(lambda x: x[1], ascending= False)

    results = sortedMovies.take(5)
    for result in results:
        print(movieNames[result[0]], result[1])
    time_elapsed = time.time() - start_time
    print("Runtime: ", time_elapsed)