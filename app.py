# all the imports
import os
import itertools
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['localhost'],
    port=9200,
)

app = Flask(__name__)


@app.route('/search')
def search(methods=['GET']):
    search_term = request.args.get('search', '')
    if 'vs' in search_term:
        search_terms = search_term.split("vs")
        list1 = search_in_elasticsearch(search_terms[0])
        list2 = search_in_elasticsearch(search_terms[1])
        result = list(itertools.product(list1,list2))
    else:
        result = search_in_elasticsearch(search_term)
    return result

@app.route('/item')
def item():
    item_id = request.args.get('id', '')
    result = es.get(index="poc", doc_type='model', id=item_id)['_source']
    return str(result)

def search_in_elasticsearch(search_term):
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "variants",
                            "query": {
                                "multi_match": {
                                    "query": search_term,
                                    "fields": ["features"]
                                }
                            }
                        } 
                    },
                    {
                        "nested": {
                            "path": "modelDetails",
                            "query": {
                                "multi_match": {
                                    "query": search_term,
                                    "fields": ["modelName", "makeName"]
                                }
                            }
                        }
                    }
		]
            }
        }
    } 
    result = es.search(index="poc", body=query)
    sources = []
    for doc in result["hits"]["hits"]:
        source = doc['_source']
        source[_id] = doc["_id"]
        sources.push(source)
    return sources
