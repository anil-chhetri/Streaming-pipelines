from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def create_spark_session():
    """Create a Spark session configured for Kafka integration"""
    return (SparkSession.builder
            .appName("KafkaSparkIntegration")
            .config("spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,"
                    "org.apache.kafka:kafka-clients:3.3.1")
            .config("spark.sql.streaming.checkpointLocation", "/opt/spark-data/checkpoints")
            .getOrCreate())

def define_schema():
    """Define the schema for the user events data"""
    return StructType([
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("category", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("quantity", IntegerType(), True)
    ])

def read_from_kafka(spark):
    """Read streaming data from Kafka"""
    return (spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "kafka:9092")
            .option("subscribe", "user-events")
            .option("startingOffsets", "earliest")
            .load())

def process_stream(raw_stream, schema):
    """Process the raw Kafka stream into a structured format"""
    # Parse the JSON data
    parsed_stream = (raw_stream
                    .select(from_json(col("value").cast("string"), schema).alias("data"))
                    .select("data.*")
                    .withColumn("event_timestamp", to_timestamp(col("event_time"))))
    
    return parsed_stream

def analyze_events(parsed_stream):
    """Perform various analyses on the events stream"""
    
    # 1. Count events by type
    event_counts = (parsed_stream
                   .withWatermark("event_timestamp", "10 minutes")
                   .groupBy(window(col("event_timestamp"), "1 minute"), col("event_type"))
                   .count()
                   .orderBy("window", "count"))
    
    # 2. Calculate revenue by category
    revenue = (parsed_stream
              .filter(col("event_type") == "purchase")
              .withColumn("revenue", col("price") * col("quantity"))
              .withWatermark("event_timestamp", "10 minutes")
              .groupBy(window(col("event_timestamp"), "5 minutes"), col("category"))
              .agg(sum("revenue").alias("total_revenue"))
              .orderBy("window", col("total_revenue").desc()))
    
    # 3. Find popular products
    popular_products = (parsed_stream
                       .filter(col("event_type").isin("view", "cart", "purchase"))
                       .withColumn("score", when(col("event_type") == "view", 1)
                                           .when(col("event_type") == "cart", 5)
                                           .when(col("event_type") == "purchase", 10)
                                           .otherwise(0))
                       .withWatermark("event_timestamp", "10 minutes")
                       .groupBy(window(col("event_timestamp"), "5 minutes"), col("product_id"))
                       .agg(sum("score").alias("popularity_score"))
                       .orderBy("window", col("popularity_score").desc()))
    
    return event_counts, revenue, popular_products

def start_queries(event_counts, revenue, popular_products):
    """Start the streaming queries"""
    
    # Output event counts to console
    query1 = (event_counts.writeStream
             .outputMode("complete")
             .format("console")
             .option("truncate", False)
             .start())
    
    # Output revenue to console
    query2 = (revenue.writeStream
             .outputMode("complete")
             .format("console")
             .option("truncate", False)
             .start())
    
    # Output popular products to console
    query3 = (popular_products.writeStream
             .outputMode("complete")
             .format("console")
             .option("truncate", False)
             .start())
    
    return [query1, query2, query3]

def main():
    """Main function to run the Spark Streaming application"""
    print("Starting Spark Streaming application...")
    
    # Create Spark session
    spark = create_spark_session()
    
    # Define schema for the data
    schema = define_schema()
    
    # Read from Kafka
    raw_stream = read_from_kafka(spark)
    
    # Process the stream
    parsed_stream = process_stream(raw_stream, schema)
    
    # Analyze events
    event_counts, revenue, popular_products = analyze_events(parsed_stream)
    
    # Start the queries
    queries = start_queries(event_counts, revenue, popular_products)
    
    # Wait for any of the queries to terminate
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()