import random, sys
import elasticsearch1 as ES
from elasticsearch1 import helpers
sys.path.append('../')
from util import *

def search(time_s, time_e, host, index, host_t):
    global es_client

    time_start = time_s[:10] + 'T' + time_s[11:] + '.000Z'
    time_end = time_e[:10] + 'T' + time_e[11:] + '.000Z'
    #print time_start,"   ",time_end
    host_all = '20.0.8.' + str(host_t)
    index_all = "logstash-" + index
    ES_SERVERS = [{'host' : host_all, 'port': 9200}]

    es_client = ES.Elasticsearch(hosts = ES_SERVERS)

    es_search_options = set_search_optional(time_start, time_end, host)
    es_result = get_search_result(es_search_options, index_all)
    
    #print es_result


    final_result_message, final_result_time = get_result_list(es_result)
    return final_result_message,final_result_time

def search_le(time_std, host, index, host_t):
    time_start = time_std[:10] + "T" + time_std[11:] + ".000Z"
    time_end = time_std[:10] + "T" + time_std[11:] + ".000Z"
    #print time_start,"   ",time_end
    host_all = "20.0.8."+str(host_t)
    ES_SERVERS = [{
                    'host': host_all,
                        'port': 9200
                  }]
    global es_client
    es_client = ES.Elasticsearch(hosts = ES_SERVERS)
    index_all = "logstash-" + index
    es_search_options = set_search_optional_le(time_start, time_end, host)
    es_result = get_search_result(es_search_options, index_all)
    final_result_message, final_result_time = get_result_list(es_result)
    return final_result_message, final_result_time

def search_gt(time_std, host, index, host_t):
    time_start=time_std[:10]+"T"+time_std[11:]+".000Z"
    time_end=time_std[:10]+"T"+time_std[11:]+".000Z"
    #print time_start,"   ",time_end
    host_all = "20.0.8."+str(host_t)
    ES_SERVERS = [{
                    'host': host_all,
                        'port': 9200
                  }]
    global es_client
    es_client = ES.Elasticsearch(
            hosts=ES_SERVERS
                        )
            
    index_all = "logstash-" + index

    es_search_options = set_search_optional_gt(time_start, time_end, host)
    es_result = get_search_result(es_search_options, index_all)
    final_result_message,final_result_time = get_result_list(es_result)
    return final_result_message,final_result_time

def get_result_list(es_result):
    final_result_host = []
    final_result_message = []
    final_result_time = []
    index = 0
    for item in es_result:
        index += 1
        #print item
        final_result_message.append(str(item['_source']['message']))                                                            
        #final_result_host.append(str(item['_source']['host']))
        final_result_time.append(str(item['_source']['@timestamp']))
    return final_result_message,final_result_time


def get_search_result(es_search_options, index, scroll ='3m', raise_on_error = True, preserve_order = False, doc_type = 'redis-input', timeout = '1m'):                                           
    es_result = helpers.scan(
            client = es_client,
            query = es_search_options,
            scroll = scroll,
            index = index,
            doc_type = doc_type,
            timeout=timeout
            )
    return es_result

def set_search_optional(time_start, time_end, host):
    match_query = []
    for i in xrange(len(host)):
        match_query.append({"match":{"host": host[i]}})
    #print match_query
    #print time_start,"   ",time_end
    #es_search_options = {
    #    "query":{
    #        "bool": {
    #            "should":[
    #              match_query
    #              ]
    #        },
    #}
    #}
    #es_search_options={
    #    "query":{
    #        "match_all":{}
    #    }
    #}
    es_search_options = {
        "query":{
            "bool":{
                "must":[
                    {"range":{
                        "@timestamp":{
                            "gt":time_start,
                            "lt":time_end
                        }
                    }},
                ],
            }
            }
        }

    return es_search_options

def set_search_optional_le(time_start,time_end,host):
    es_search_options = {
        "query":{
            "bool": {
                "must": [
                    {"range":{
                        "@timestamp":{
                            "le":time_start
                        }
                     }}
                    ],
                }
        }
        }
    return es_search_options

def set_search_optional_gt(time_start,time_end,host):
    es_search_options = {
        "query":{
            "bool": {
                "must": [
                    {"range":{
                        "@timestamp":{
                            "gt":time_start
                        }
                     }}
                    ],
                }
        }
        }
    return es_search_options

if __name__ == '__main__':
    time_s='2017-11-17 08:00:00'
    time_e='2017-11-17 08:00:01'
    host = get_host_ip_list()
    
    index = '2017.11.17'
    host_t = 87
    final_results, result_time = search(time_s, time_e, host, index, host_t)
    #print host
    #print len(final_results)
    #print final_results
    print result_time
    #print len(final_results[0]) 
    #print len(final_results[1]) 
    #for item in final_results[0]:
    #    print item
