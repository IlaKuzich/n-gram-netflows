import pika
import json
import logging
from datetime import datetime
from listener import Listener


class Consumer:
    def __init__(self, connection, queue_name, n_flows, window_size):
        self.channel = connection.channel()
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.on_message, auto_ack=True)
        self.n_flows = n_flows
        self.index = 0
        self.window_size = window_size
        self.flows = {}
        self.listeners = []

    def start_consuming(self):
        print(' [*] Waiting for messages.')
        self.channel.start_consuming()

    def register(self, listener: Listener):
        self.listeners.append(listener)

    def dispatch(self):
        for peer in self.flows:
            data = self.flows[peer]['data']
            batch_size = len(data) - len(data) % self.window_size
            if batch_size < self.window_size:
                continue
            for listener in self.listeners:
                listener.handle(peer, data[:batch_size])
            self.flows[peer]['data'] = data[batch_size:]

    def on_message(self, channel, method_frame, header_frame, body):
        try:
            netflow = json.loads(body.decode())
            netflow['StartTimeDecoded'] = self.to_timestamp(netflow)
            src_peer = netflow['SrcAddr']
            if src_peer not in self.flows:
                self.flows[src_peer] = {
                    'data': [],
                    'last_appended': datetime.min
                }
            if (netflow['StartTimeDecoded'] - self.flows[src_peer]['last_appended']).seconds > 15:
                self.flows[src_peer]['data'].append('<idle>')
            self.flows[src_peer]['data'].append(netflow)
            self.flows[src_peer]['last_appended'] = netflow['StartTimeDecoded']
        except:
            logging.warning('Invalid netflow was consumed')
        self.index += 1
        if self.n_flows <= self.index:
            self.dispatch()
            self.index = 0

    def to_timestamp(self, row):
        return datetime.strptime(row['StartTime'], "%Y/%m/%d %H:%M:%S.%f")
