### main application file for jiminy-modeller ###
import psycopg2
import pyspark
from pyspark.sql import SQLContext
from pyspark import SparkContext, SparkConf
import math

import modeller
####

######### put this into some kind of nice method
conf = SparkConf().setAppName("recommender")
conf = (conf.setMaster('local[*]')
        .set('spark.executor.memory', '4G')
        .set('spark.driver.memory', '45G')
        .set('spark.driver.maxResultSize', '10G'))
sc = SparkContext(conf=conf)
sqlContext=SQLContext(sc)
#print "Set up SQL Context"
try:
    con = psycopg2.connect(dbname='movielens', user='postgres', host='localhost', port='5432', password='password')
#    print "Connected to database"
except:
    print "Cannot connect to the database"


######################


cursor=con.cursor()
cursor.execute("SELECT * FROM ratingsdata")

ratings = cursor.fetchall()

### Do I need to close the cursor?

#creates the RDD:
ratingsRDD = sc.parallelize(ratings)
ratingsRDD = ratingsRDD.map(lambda x: (x[0], x[1], x[2]))
########## TRAINING A MODEL ###############

### get a good look at Rui's code from here on.

rank = 5
iterations = 1
seed = 42
def split_sets(ratings, proportions):
    split = ratings.randomSplit(proportions)
    return {'training': split[0], 'validation': split[1], 'test': split[2]}
sets = split_sets(ratingsRDD, [0.63212056, 0.1839397, 0.1839397])
print "got dem sets"
print "have set the tuning params and split the data"


estimator = modeller.Estimator(ratingsRDD)
parameters = estimator.run(ranks=[2, 4],
                           lambdas=[0.01, 0.05],
                           iterations=[2,5])

model = modeller.Trainer(data=ratingsRDD,
                         rank=parameters['rank'],
                         iterations=parameters['iteration'],
                         lambda_ = parameters['lambda'],
                         seed=42).train()