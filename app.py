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
cors = CORS(app, resources={r"/*": {"origins": "*","supports_credentials": True}})

@app.route('/search')

def search(methods=['GET']):
    search_term = request.args.get('q', '')
    print search_term
    if 'vs' in search_term:
        search_terms = search_term.split("vs")
        list1 = search_in_elasticsearch(search_terms[0])
        list2 = search_in_elasticsearch(search_terms[1])
	if not (list1 and list2):
	    result = [[list1, list2]]	
        else: 
	    result = list(itertools.product(list1,list2))
    else:
	result = search_in_elasticsearch(search_term)
    return json.dumps(result)

@app.route('/item')
def item():
    item_id = request.args.get('id', '')
    result = es.get(index="poc", doc_type='model', id=item_id)['_source']
    return  json.dumps(result)

@app.route('/listing')
def listing():
    results= [es.get(index="poc", doc_type='model', id=item_id)['_source'] for item_id in range(1, 5)] 
    return  json.dumps(results)


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

@app.route("/suggest")
def suggest(methods=['GET']):
    
    search_term = request.args.get('q', '')

    # Search for BRAND
    data = postReq(json.dumps({"query":search_term, "filter":{"brand":1}, "bucket":{},"limit":2}))
    #print data
    json_data = json.loads(postReq(json.dumps({"query":search_term, "filter":{"brand":1}, "bucket":{},"limit":2})))
    #print json_data
    start = 0
    output = {}
    for data in json_data:

        output[start] = data["matched"]
        start = start + 1

    # Search for MODEL
    json_data1 = json.loads(
        postReq(json.dumps({"query": search_term, "filter": {"model": 1}, "bucket": {}, "limit": 2})))

    for data in json_data1:

        output[start] = data["matched"]
        start = start + 1

    # Search for VERSION
    json_data = json.loads(
        postReq(json.dumps({"query": search_term, "filter": {"version": 1}, "bucket": {}, "limit": 2})))

    for data in json_data:
        output[start] = data["matched"]
        start = start + 1

    # Search for COMPARE
    json_data = json.loads(
        postReq(json.dumps({"query": search_term, "filter": {"compare": 1}, "bucket": {}, "limit": 2})))

    for data in json_data:
        output[start] = data["matched"]
        start = start + 1

    returnStr = ""
    if start > 0:
        return Response(json.dumps(output), content_type='application/json; charset=utf-8')

    splitArr = search_term.split(" ")
    length = len(splitArr)
    if start == 0:

        if length == 1:
            # Search for COMPARE
            json_data = json.loads(
                postReq(json.dumps({"query": search_term, "filter": {"attributes": 1}, "bucket": {}, "limit": 1})))
            for data in json_data:
                output[start] = data["matched"]
                intelligentFilter = data["matched"].lower()
                intelligent = json.loads(
                    postReq(json.dumps({"query": "", "filter": {intelligentFilter: 2}, "bucket": {}, "limit": 3})))
                start =start + 1
                for individualData in intelligent:
                    output[start] = individualData["matched"]
                    start = start + 1

                intelligent = json.loads(
                    postReq(json.dumps({"query": "", "filter": {intelligentFilter: 1}, "bucket": {}, "limit": 3})))
                start = start + 1
                for individualData in intelligent:
                    output[start] = individualData["matched"]
                    start = start + 1

    if start == 0:
        if length > 0:
            last = splitArr[length -1]
            json_data = json.loads(
                postReq(json.dumps({"query": last, "filter": {"attributes": 1}, "bucket": {}, "limit": 4})))
            for data in json_data:
                splitArr = splitArr[:-1]
                output[start] = " ".join(splitArr)+" "+data["matched"]
                start = start + 1

    return Response(json.dumps(output), content_type='application/json; charset=utf-8')

def postReq(req):
    url = "http://127.0.0.1:1081/query"

    payload = req

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "28d95f1e-3976-b2bd-3b3e-990ec56389d8"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response.text
