from consumer import Consumer
from listener import Listener
import logging
import pika
import sys, os

connection_str = os.getenv('RABBIT_MQ_HOST')
queue_name = os.getenv('RABBIT_MQ_QUEUE')
output_queue_name = os.getenv('RABBIT_MQ_OUTPUT_QUEUE')

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)

        flow_buffer_size = int(os.getenv('FLOW_BUFFER_SIZE'))
        window_size = int(os.getenv('WINDOW_SIZE'))
        step_size = int(os.getenv('STEP_SIZE'))
        N = int(os.getenv('N_GRAM_ORDER'))
        anomaly_threshold = float(os.getenv('ANOMALY_THRESHOLD'))
        warning_threshold = float(os.getenv('WARNING_THRESHOLD'))
        bot_threshold = float(os.getenv('BOT_THRESHOLD'))
        attenuation = float(os.getenv('ATTENUATION'))

        parameters = pika.URLParameters(connection_str)
        connection = pika.BlockingConnection(parameters)

        consumer = Consumer(connection, queue_name, n_flows=flow_buffer_size, window_size=window_size)
        listener = Listener(N=N,
                            window=window_size,
                            step=step_size,
                            anomality_threshold=anomaly_threshold,
                            warn_threshold=warning_threshold,
                            bot_threshold=bot_threshold,
                            attenuation=attenuation,
                            connection=connection,
                            output_queue=output_queue_name)
        consumer.register(listener)

        consumer.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
