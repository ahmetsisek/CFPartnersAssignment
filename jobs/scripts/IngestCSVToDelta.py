import datetime
import uuid
import sys

from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from delta import *
from delta.tables import *
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType

if __name__ == "__main__":
    spark = SparkSession.builder.appName("IngestCSVToDelta") \
                                .getOrCreate()

    input_path = sys.argv[1] # path to CSV files
    output_path = sys.argv[2] # path to Delta table
    header = sys.argv[3] # Data with header or not 

    if header == 'true':
        df = spark.read.option("header", "true").csv(input_path)
    else:
        schema = StructType([StructField("person_id", IntegerType(), True),
                             StructField("person_name", StringType(), True),
                             StructField("birth_year", IntegerType(), True),
                             StructField("occupation", StringType(), True)])
        df = spark.read.csv(input_path,header=False,schema=schema)

    # Add additional columns
    df = df.withColumn("ingestion_tms", lit(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    df = df.withColumn("batch_id", lit(str(uuid.uuid4())))

    try:
        # Read Delta Table
        deltaTablePeople = DeltaTable.forPath(spark, output_path)
    except:
        # If Delta Table is not there, initialize it with append
        df.write.format("delta").mode("append").save(output_path)
        deltaTablePeople = DeltaTable.forPath(spark, output_path)

    # Merge
    deltaTablePeople.alias('people') \
    .merge(
        df.alias('updates'),
        'people.person_id = updates.person_id'
    ) \
    .whenMatchedUpdate(set =
        {
        "person_id": "updates.person_id",
        "person_name": "updates.person_name",
        "birth_year": "updates.birth_year",
        "occupation": "updates.occupation",
        "ingestion_tms": "updates.ingestion_tms",
        "batch_id": "updates.batch_id"
        }
    ) \
    .whenNotMatchedInsert(values =
        {
        "person_id": "updates.person_id",
        "person_name": "updates.person_name",
        "birth_year": "updates.birth_year",
        "occupation": "updates.occupation",
        "ingestion_tms": "updates.ingestion_tms",
        "batch_id": "updates.batch_id"
        }
    ) \
    .execute()
    
    df_output = spark.read.format('delta').load(output_path)
    print("Output Dataset:")
    df_output.show(10, False) # Just to check if everything is fine

    spark.stop()
