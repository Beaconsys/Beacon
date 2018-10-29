import elasticsearch1 as es
from elasticsearch1 import helpers 

def scroll_search(query, host, index_name):
    ES_SERVERS = [{
        'host': host,
        'port': 9200
    }]

    es_client = es.Elasticsearch(
        hosts=ES_SERVERS
    )

    es_result = get_search_result(query, index_name, es_client)

    return es_result

def get_search_result(es_search_options, index_name, es_client, 
                      scroll='5m', raise_on_error=True, preserve_order=False, 
                      doc_type='redis-input', timeout="1m"):

    es_result = helpers.scan(
        client=es_client,
        query=es_search_options,
        scroll=scroll,        
        index=index_name,
        doc_type=doc_type,
        timeout=timeout
    )
   
    return es_result
#Test main
if __name__ == "__main__":
    es_result = scroll_search( { "query" : { "match_all": {} } }, "20.0.2.201", "logstash-2018.03.18")
    count = 0
    for item in es_result:
        count += 1
        print item
    print count
