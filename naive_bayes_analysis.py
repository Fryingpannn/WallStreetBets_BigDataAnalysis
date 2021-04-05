from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
# $example off$
from pyspark.sql import SparkSession
from pyspark.sql.functions import split as splitsp
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import StopWordsRemover

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("NaiveBayesExample")\
        .getOrCreate()


    # $example on$
    # Load training data
    df = spark.read.csv("Data/7days-updated-wsbdata.csv",header='true')
    _df = df.withColumn(colName="text_vector",col = splitsp(df.text," "))

    #Removing stop words
    remover = StopWordsRemover(inputCol="text_vector", outputCol="filtered")
    filtered_df = remover.transform(_df)
    #i have filtered col


    #CountVecotrizing with filtered DF
    cv = CountVectorizer(inputCol="filtered",outputCol="features")
    model = cv.fit(filtered_df)
    print(len(model.vocabulary))
    result = model.transform(filtered_df)

    print(result.first().features.toArray())
    #print(type(result.features))


    #result1 = transform(result)

    #result2 = transform(result)


    #count_vectorizer = CountVectorizer(inputCol=_df.text_vector,outputCol="features",stop_words="English")
    
    spark.stop()