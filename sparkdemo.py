from pyspark.sql import SparkSession

# Conectar con Spark Master
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("DemoTest") \
    .getOrCreate()

# Crear un RDD de prueba (números del 1 al 10)
rdd = spark.sparkContext.parallelize(range(1, 11))
suma = rdd.sum()
print(f"La suma de 1 a 10 es: {suma}")

spark.stop()
