# from: https://gist.github.com/jianyu0503/4753344051572c8fc7aa18123eafd2cc

from pyspark import SparkContext
from pyspark.sql import SQLContext, Row

def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sparkContext)
    return globals()['sqlContextSingletonInstance']


def find_most_tag(sc, tags_file):
    """Load data from tags.csv"""
    df = getSqlContextInstance(sc).read. \
         format('com.databricks.spark.csv'). \
         options(header='true', inferschema='true'). \
         load(tags_file)

    # Set df table name as tag #
    df.registerTempTable("tag")

    # Finds the most common tag for a movie title #
    getSqlContextInstance(sc).sql("""SELECT tag, count(`tag`) as cnt 
                                     FROM tag 
                                     GROUP BY `tag` 
                                     ORDER BY cnt DESC 
                                     LIMIT 1""").show()

def find_most_genre(sc, ratings_file, movies_file):

    # Load data from ratings.csv #
    df2 = getSqlContextInstance(sc).read.\
          format('com.databricks.spark.csv').\
          options(header='true', inferschema='true').\
          load(ratings_file)

    # Set df2 table name as rating #
    df2.registerTempTable("rating")

    # Load data from movies.csv #
    df3 = getSqlContextInstance(sc).read.\
          format('com.databricks.spark.csv').\
          options(header='true', inferschema='true').\
          load(movies_file)

    # Set df3 table name as movie #
    df3.registerTempTable("movie")

    # Join rating table and movie table by movieId #
    df4 = getSqlContextInstance(sc).sql("""SELECT movie.movieId, movie.genres, rating.rating 
                                           FROM rating 
                                           INNER JOIN movie 
                                           ON rating.movieId = movie.movieId""")

    # Set df4 table name as joined_table #
    df4.registerTempTable("joined_table")

    # Finds the most common genre rated by a user #
    getSqlContextInstance(sc).sql("""SELECT genres, count(`genres`) as cnt 
                                     FROM joined_table 
                                     GROUP BY `genres` 
                                     ORDER BY cnt DESC 
                                     LIMIT 1""").show()
def main():
    """ Change File Path before Submission"""
    tags_file = "/gfs/ml-20m/tags.csv"
    ratings_file = "/gfs/ml-20m/ratings.csv"
    movies_file = "/gfs/ml-20m/movies.csv"

    sc = SparkContext(appName="Exercise")
    find_most_tag(sc, tags_file)
    find_most_genre(sc, ratings_file, movies_file)

    sc.stop()

if __name__ == "__main__":
    main()