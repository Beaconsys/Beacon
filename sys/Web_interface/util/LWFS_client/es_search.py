# uncompyle6 version 3.1.2
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Aug  4 2017, 00:39:18) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-16)]
# Embedded file name: /home/export/mount_test/swstorage/taihu-io/job_query_script/es_search.py
# Compiled at: 2018-01-25 19:04:28
from elasticsearch1 import helpers
import sys
import elasticsearch1 as ES, random
from scroll_query import scroll_search, get_search_result

def search(time_start, time_end, host, index, host_t):
    host_t = random.randint(10, 60)
    host_all = '20.0.8.' + str(host_t)
    index_all = 'logstash-' + index
    es_search_options = set_search_optional(time_start, time_end, host)
    es_result = scroll_search(es_search_options, host_all, index_all)
    final_result_message, final_result_host = get_result_list(es_result)
    return (
     final_result_message, final_result_host)


def get_result_list(es_result):
    final_result_host = []
    final_result_message = []
    index = 0
    for item in es_result:
        index += 1
        final_result_message.append(str(item['_source']['message']))
        final_result_host.append(str(item['_source']['host']))

    return (final_result_message, final_result_host)


def set_search_optional(time_start, time_end, host):
    match_query = []
    for i in xrange(len(host)):
        match_query.append({'match': {'host': host[i]}})

    es_search_options = {'query': {'bool': {'must': [
                                 {'bool': {'should': [
                                                      match_query]}},
                                 {'range': {'@timestamp': {'gt': time_start, 
                                                             'lt': time_end}}}], 
                          'should': [{'match': {'message': 'OPEN'}}, {'match': {'message': 'RELEASE'}}, {'match': {'message': 'READ'}}, {'match': {'message': 'WRITE'}}]}}}
    return es_search_options


if __name__ == '__main__':
    final_results = search(time_start, time_end, host)
    print len(final_results)
# okay decompiling es_search.pyc
