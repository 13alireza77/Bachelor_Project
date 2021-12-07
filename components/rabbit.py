import json
import time

import pika

from config.config import Config


class RabbitConnection:
    _connection_name = None
    _exchange = None
    _route = None
    _queue_name = None

    def __init__(self, _connection_name="rabbit"):
        config = Config()
        host = config.get(_connection_name, 'host')
        port = config.get(_connection_name, 'port')
        username = config.get(_connection_name, 'username')
        password = config.get(_connection_name, 'password')
        queue_size = int(config.get(_connection_name, 'queue_size'))
        while True:
            try:
                credentials = pika.PlainCredentials(username, password)
                rabbit_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, port=port, credentials=credentials))
                self.channel = rabbit_connection.channel()
                break
            except:
                time.sleep(5)

        self.channel.queue_declare(queue=self._queue_name, durable=True, arguments={'x-max-length': queue_size})
        self.channel.exchange_declare(exchange=self._exchange, exchange_type='direct')
        self.channel.queue_bind(exchange=self._exchange, routing_key=self._route, queue=self._queue_name)

    def refresh_connection(self):
        config = Config()
        host = config.get(self._connection_name, 'host')
        port = config.get(self._connection_name, 'port')
        username = config.get(self._connection_name, 'username')
        password = config.get(self._connection_name, 'password')
        while True:
            try:
                credentials = pika.PlainCredentials(username, password)
                rabbit_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, port=port, credentials=credentials))
                self.channel = rabbit_connection.channel()
                break
            except:
                time.sleep(5)

    def push(self, data: dict):
        while True:
            try:
                self.channel.basic_publish(exchange=self._exchange, properties=pika.BasicProperties(delivery_mode=2),
                                           routing_key=self._route, body=json.dumps(data))
                break
            except:
                self.refresh_connection()

    def create_bind(self, queue, exchange, exchange_type, routing_key):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
        self.channel.queue_bind(exchange=exchange,
                                queue=queue,
                                routing_key=routing_key)

    def get_len_queue(self):
        while True:
            try:
                q = self.channel.queue_declare(queue=self._route, durable=True)
                return q.method.message_count
            except:
                self.refresh_connection()

    def basic_get(self):
        while True:
            try:
                method_frame, header_frame, body = self.channel.basic_get(queue=self._queue_name)
                self.channel.basic_ack(method_frame.delivery_tag)
                return body
            except:
                self.refresh_connection()

    # def basic_ack(self, delivery_tag):
    #     with RabbitConnection(self.connection_name) as r:
    #         r.channel.basic_ack(delivery_tag)

    def insert_many_rabbit(self, list_data):
        while True:
            try:
                data_len = len(list_data) - 1
                while data_len >= 0:
                    try:
                        self.channel.basic_publish(exchange=self._exchange,
                                                   routing_key=self._route,
                                                   body=list_data[data_len],
                                                   properties=pika.BasicProperties(
                                                       delivery_mode=2,
                                                   ))
                        data_len -= 1
                    except:
                        self.refresh_connection()
                break
            except:
                self.refresh_connection()
