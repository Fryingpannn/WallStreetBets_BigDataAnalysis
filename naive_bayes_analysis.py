from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
# $example off$
from pyspark.sql import SparkSession
from pyspark.sql.functions import split as splitsp
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("NaiveBayesExample")\
        .getOrCreate()


    # $example on$
    # Load training data
    df = spark.read.csv("Data/updated-30dayswsb.csv",header='true')
    _df = df.withColumn(colName="text_vector",col = splitsp(df.text," "))

    #Removing stop words
    remover = StopWordsRemover(inputCol="text_vector", outputCol="filtered")
    filtered_df = remover.transform(_df)
    #i have filtered col


    #CountVecotrizing with filtered DF
    cv = CountVectorizer(inputCol="filtered",outputCol="features")
    model = cv.fit(filtered_df)
    #print(model.vocabulary)
    result = model.transform(filtered_df)

    kmeans = KMeans().setK(3).setSeed(2)
    model = kmeans.fit(result.select("features"))

    predictions = model.transform(result.select("features"))
    evaluator = ClusteringEvaluator()
    silhouette = evaluator.evaluate(predictions)

    # Shows the result.
    centers = model.clusterCenters()

    #probably model.data? [[0,10,20],[30,40,60]......]
    # for : for: print vol[0],vol[10]
    print("Cluster Centers: ")
    for center in centers:
        print(center)


    #count_vectorizer = CountVectorizer(inputCol=_df.text_vector,outputCol="features",stop_words="English")
    
    spark.stop()