#!/usr/bin/env python
import threading, time
from kafka import KafkaConsumer, KafkaProducer
import os,json
import logging

KAFKA_URI=os.environ.get("KAFKA_URI", default=False)

class IkaProducer():
    def __init__(self,topic_name,data):
        self.topic_name = topic_name
        self.data = data

    def run(self):
        producer = KafkaProducer(bootstrap_servers=KAFKA_URI,value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        # produce asynchronously with callbacks
        producer.send(self.topic_name, self.data).add_callback(self.on_send_success).add_errback(self.on_send_error)
        time.sleep(1)

        # block until all async messages are sent
        producer.flush()
    
    @staticmethod
    def on_send_success(record_metadata):
        logging('topic: %s',record_metadata.topic)
        logging('partition: %s',record_metadata.partition)
        logging('offset: %s',record_metadata.offset)
    
    @staticmethod
    def on_send_error(excp):
        logging.error('I am an errback', exc_info=excp)
    # handle exception