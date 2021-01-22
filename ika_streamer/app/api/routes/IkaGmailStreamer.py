from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, File, UploadFile
from starlette.responses import FileResponse
from ikamail.GmailHelper import GmailHelper
from app.api.models.Gmail.GmailCollecterModel import GmailCollecterModel

from app.api.models.Consumer.IkaConsumer import IkaConsumer
from app.api.models.Producer.IkaProducer import IkaProducer
from app.api.models.Gmail.GmailSchema import GmailOut
from kafka import KafkaConsumer, TopicPartition
from bson.json_util import dumps
from typing import List
from pandas.io.json import json_normalize
from pandas import DataFrame
from kafka.admin import NewTopic
from kafka import KafkaAdminClient
import pandas as pd
import json, time
import logging
import os 
from fastapi.responses import HTMLResponse,JSONResponse
from json import loads


KAFKA_URI=os.environ.get("KAFKA_URI", default=False)

GmailStreamersApi = APIRouter()
                
@GmailStreamers.get('/getMessageId')
async def getMessageId(batch_using: bool=True, transform_flag: bool=True, include_spam_trash: bool=False, max_results:int=200, max_workers:int=100, file_return:str=None):
    """
    create_stream: 

    Args:
    
        batch_using (bool, optional): if Flag False -> Take nextPageToken else True -> Take by batch. Defaults to True.
        transform_flag (bool, optional): Using this flag if you want used Transformer Model. Defaults to True.
        include_spam_trash (bool, optional): Include messages from SPAM and TRASH in the results.. Defaults to False.
        max_results (int, optional): Maximum number of messages to return.. Defaults to 25.
        max_workers (int, optional): Maximun number of worker used by multithreading. Defaults to 25.
        file_return (str, optional): Type of file returned by API. Defaults to None.

    Raises:
    
        HTTPException: [description]

    Returns:
    
        API, Json, Csv: Return streaming data from Ika's streamer
    """
    data = []
    
    message_id = GmailHelper("prod").get_message_id(
        "me",
        include_spam_trash=include_spam_trash,
        max_results=max_results,
        batch_using=batch_using
    )
    
    topic_name = 'mirana-mail-id'
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_URI)
        
        # Remplacer le name de new topcis par adresse email ou ID unique
        topic = NewTopic(name=topic_name,num_partitions=4,replication_factor=2)
        admin.create_topics(topic_name)
        
    except Exception:
        pass
    

    IkaProducer(topic_name, message_id).run()
    
    consumer = KafkaConsumer(
        topic_name,                                # specify topic to consume from
        bootstrap_servers=KAFKA_URI,
        consumer_timeout_ms=3000,                       # break connection if the consumer has fetched anything for 3 secs (e.g. in case of an empty topic)
        auto_offset_reset='earliest',                   # automatically reset the offset to the earliest offset (should the current offset be deleted or anything)
        enable_auto_commit=False,                        # offsets are committed automatically by the consumer
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    logging.info('Consumer constructed')
        
    try:
        for message in consumer:                            # loop over messages

            print("Offset: ",message.offset)
            x = message.value
            data.append(x)
            
        consumer.close()
        
        return JSONResponse(content=data)
    
    except Exception as e:
        print(e)
        logging.info('Error: '+e)