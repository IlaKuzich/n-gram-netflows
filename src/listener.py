from model import Model
from encoder import encode
import pickle
import pika
import json
import logging

class Listener:
    def __init__(self, N, window, step, anomality_threshold, warn_threshold, bot_threshold, attenuation, connection, output_queue):
        logging.info('Start model initialization')
        with open('./pretrained/vocab.txt', 'rb') as vocab_file:
            vocab = pickle.load(vocab_file)

        with open('./pretrained/counts.txt', 'rb') as counts_file:
            counts = pickle.load(counts_file)

        self.model = Model(N, window, step, vocab, counts)
        logging.info('Model initialized')

        self.anomality_threshold = anomality_threshold
        self.warn_threshold = warn_threshold
        self.bot_threshold = bot_threshold
        self.attenuation = attenuation
        self.window = window
        self.step = step

        self.statistic = {}

        self.channel = connection.channel()
        self.channel.queue_bind(queue=output_queue, exchange='sensor_out', routing_key='detection')

    def handle(self, peer, netflows):
        encoded_flows = encode(netflows)
        if peer not in self.statistic:
            self.statistic[peer] = {
                'score': 1.0,
                'flows': []
            }
        flows_to_store = self.statistic[peer]['flows']
        score = self.statistic[peer]['score']
        estimations = self.model.evaluate_chain(encoded_flows)
        for i in range(len(estimations)):
            anomality_estimation = self.attenuation
            perplexity = estimations[i]
            if perplexity / self.anomality_threshold >= 1:
                anomality_estimation = perplexity / self.anomality_threshold
            score *= anomality_estimation

            if score > self.warn_threshold:
                flows_to_store.extend(netflows[i * self.step:i * self.step + self.window])
                if score > self.bot_threshold:
                    self.push_anomaly_messages(flows_to_store)
                    flows_to_store = []
                    if score > self.bot_threshold * 10:
                        score = self.bot_threshold * 10
            elif score <= self.warn_threshold and len(flows_to_store) > 0:
                print('Warn log:', len(flows_to_store)) # send warn logs to net dataset candidates
                flows_to_store = []
        if score < 1:
            score = 1
        if score > 1:
            logging.info('Score is: {} for peer {}'.format(score, peer))
        self.statistic[peer] = {
            'score': score,
            'flows': flows_to_store
        }

    def push_anomaly_messages(self, flows):
        for flow in flows:
                if flow == '<idle>':
                    continue
                del flow['StartTimeDecoded']
                self.channel.basic_publish(exchange='sensor_out', routing_key='detection', body=json.dumps(flow))


