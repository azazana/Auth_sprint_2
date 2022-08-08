import time
from elasticsearch import Elasticsearch
import os

es = Elasticsearch(hosts=os.getenv("ELASTIC_HOST") + ":" + os.getenv("ELASTIC_PORT"))

while not es.ping():
    time.sleep(3)

print("Ok ES")
