# all the imports
import os
import json
import itertools
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from elasticsearch import Elasticsearch
import requests
from flask_cors import CORS, cross_origin
ES_HOST = 'elasticsearch'
ES_PORT = 9200

es = Elasticsearch(
    [ES_HOST],
    port=ES_PORT,
)
app = Flask(__name__)
CORS(app)

@app.route('/search')
@cross_origin()
def search(methods=['GET']):
    search_term = request.args.get('q', '')
    print search_term
    if 'vs' in search_term:
        search_terms = search_term.split("vs")
	print search_terms
        list1 = search_in_elasticsearch(search_terms[0])
        list2 = search_in_elasticsearch(search_terms[1])
        result = list(itertools.product(list1,list2))
    else:
	result = search_in_elasticsearch(search_term)
    return json.dumps(result)

@app.route('/item')
def item():
    item_id = request.args.get('id', '')
    result = es.get(index="poc", doc_type='model', id=item_id)['_source']
    return  json.dumps(result)

def search_in_elasticsearch(search_term):
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": search_term,
                            "fields": ["modelDetails.modelName", "modelDetails.makeName"]
                        }
                    },
                    {
                        "nested": {
                            "path": "modelVersions",
                            "query": {
                                "multi_match": {
                                    "query": search_term,
                                    "fields": ["modelVersions.features"]
                                }
                            }
                        } 
                    }

                ]
            }
        }
    }
    #result = es.search(index="poc", doc_type='model', body= query)
    url = "http://{}:{}/poc/model/_search".format(ES_HOST, ES_PORT)
    payload = json.dumps(query) 
    headers = {
        'content-type': "application/json",
    }
    response = requests.request("GET", url, data=payload, headers=headers )
    result =  json.loads(response.text)
    sources = []
    for doc in result["hits"]["hits"]:
        source = doc['_source']
        source["id"] = doc["_id"]
        sources.append(source)
    return sources 
