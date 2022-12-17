from confluent_kafka.avro import AvroConsumer
from google.cloud import bigquery
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/path/to/json"

dataset_name = 'Bitcoin'
table_name = 'stream_Bitcoin_price_2017'

client = bigquery.Client()
client.create_dataset(dataset_name, exists_ok=True)
dataset = client.dataset(dataset_name)

schema = [
    bigquery.SchemaField('Date', 'STRING'),
    bigquery.SchemaField('Open', 'FLOAT64'),
    bigquery.SchemaField('High', 'FLOAT64'),
    bigquery.SchemaField('Low', 'FLOAT64'),
    bigquery.SchemaField('Close', 'FLOAT64'),
    bigquery.SchemaField('Volume', 'NUMERIC'),
    bigquery.SchemaField('MarketCap', 'NUMERIC')
]

table_ref = bigquery.TableReference(dataset, table_name)
table = bigquery.Table(table_ref, schema=schema)
client.create_table(table, exists_ok=True)

def read_messages():
    consumer_config = {"bootstrap.servers": "localhost:9092",
                       "schema.registry.url": "http://localhost:8081",
                       "group.id": "practice.bitcoin.avro.consumer.2",
                       "auto.offset.reset": "earliest"}

    consumer = AvroConsumer(consumer_config)
    consumer.subscribe(["practice.bitcoin_price_Training"])

    while(True):
        try:
            message = consumer.poll(5)
        except Exception as e:
            print(f"Exception while trying to poll messages - {e}")
        else:
            if message:
                print(f"Successfully poll a record from "
                      f"Kafka topic: {message.topic()}, partition: {message.partition()}, offset: {message.offset()}\n"
                      f"message key: {message.key()} || message value: {message.value()}")
                consumer.commit()
                # INSERT STREAM TO BIGQUERY
                client.insert_rows(table, [message.value()])
            else:
                print("No new messages at this point. Try again later.")

    consumer.close()


if __name__ == "__main__":
    read_messages()

