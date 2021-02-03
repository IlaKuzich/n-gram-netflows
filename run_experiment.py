import json
import pika
from util.io_utils import read_dataset_csv

connection_str = 'amqp://admin:notsosecret@localhost:5672/'


if __name__ == "__main__":
    parameters = pika.URLParameters(connection_str)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_bind(queue='netflow', exchange='synthetic_test', routing_key='test')

    test_df = read_dataset_csv([
        'CTU-13 files to analyze'
    ])

    for index, row in test_df.iterrows():
        channel.basic_publish(exchange='synthetic_test', routing_key='test', body=json.dumps(row.to_dict()))


