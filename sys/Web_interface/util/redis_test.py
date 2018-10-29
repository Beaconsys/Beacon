# -*- coding: utf-8 -*-
import sys, datetime, time, elasticsearch1 as ES, redis
from elasticsearch1 import helpers
from util import *

MBYTE = 1048576.0 # 1024 * 1024
OST_NUM = 440
height = 300
time_s = '2018-07-28 15:00:00'
time_e = '2018-07-28 15:30:00'
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

def search(time_s, time_e, index, host_t):
    time_start = time_s[:10] + 'T' + time_s[11:] + '.000Z'
    time_end = time_e[:10] + 'T' + time_e[11:] + '.000Z'
    host_all = '20.0.8.' + str(host_t)
    index_all = "logstash-" + index[0]
    ES_SERVERS = [{'host' : host_all, 'port': 9200}]
    es_client = ES.Elasticsearch(hosts = ES_SERVERS)
    es_search_options = {"query":{"bool":{"must":[{"range":{"@timestamp":{"gt":time_start,"lt":time_end}}}]}}}
    es_result = helpers.scan(
        client = es_client,
        query = es_search_options,
        scroll = '3m',
        index = index_all,
        doc_type = 'redis-input',
        timeout = '1m'
    )
    
    final_result_message = []
    final_result_time = []
   
    rlen = 0
    for item in es_result:
        rlen += 1
        final_result_message.append(str(item['_source']['message']))                                                            
        final_result_time.append(str(item['_source']['@timestamp']))

    print "RESULT LEN : " + str(rlen)
    return final_result_message, final_result_time

    
def query_ost(time_s, time_e):
    dict_r = {}
    dict_w = {}
    result = []

    stime = datetime.datetime.strptime(time_s, '%Y-%m-%d %H:%M:%S') # the query start time
    etime = datetime.datetime.strptime(time_e, '%Y-%m-%d %H:%M:%S') # the query end time

    arr_length = (etime - stime).seconds + 1

    iobw_r = [([0] * arr_length) for i in range(OST_NUM)] 
    iobw_w = [([0] * arr_length) for i in range(OST_NUM)] 
    
    index = get_index(time_s, time_e)
    host_t = 90
    try:
        query_start = time.time()
        query_result = search(time_s, time_e, index, host_t)
        query_end = time.time()
        print 'ES Query Time : ' + str(round(query_end - query_start, 2)) + ' s'
    except Exception as e:
        print e
    
    for i in xrange(len(query_result[0])):
        str_tmp = query_result[0][i] + ' ' + query_result[1][i]
        result.append(str_tmp) # message + timestamp
        
    print 'Size : ' + str(sys.getsizeof(result)/MBYTE) + ' MB'
    result.sort()

    dts = time.time()
    t0 = stime # the query start time
    r1 = result[0].replace(',','').replace('[', '').replace(']', '').split(' ') # the first record in the query result
    ost_p = int(r1[0], 16)
    try:
        time_p = datetime.datetime.strptime(str(r1[-1])[:10] + ' ' + str(r1[-1])[11:-5], '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print 'Bad time format'
    t_p = (time_p - t0).seconds
    
    read_p = 0
    write_p = 0
    for i in range(1,len(r1) - 1, 3):
        read_p += int(r1[i]) * int(r1[i+1])
        write_p += int(r1[i]) * int(r1[i+2])
    #print 'OSTID : ' + str(ost_p) + ', READ VALUE : ' + str(read_p) + ', WRITE VALUE : ' + str(write_p) + ', TIME : ' + str(time_p)

################ BEGIN TO DEAL DATA ################    
    for item in range(1, len(result)):
        try:
            record =  result[item].replace(',', '').replace('[', '').replace(']', '').split(' ') 
            ost_c = int(record[0], 16)
            time_c = datetime.datetime.strptime(str(record[-1])[:10] + ' ' + str(record[-1])[11:-5], '%Y-%m-%d %H:%M:%S')
            t_c = (time_c - t0).seconds
            read_c = 0
            write_c = 0
            for i in range(1, len(record) - 1, 3):
                read_c += int(record[i]) * int(record[i + 1])
                write_c += int(record[i]) * int(record[i + 2])
            if ost_c == ost_p:
                interval = t_c - t_p
                read_value = int(read_c) - int(read_p)
                write_value = int(write_c) - int(write_p)
                if interval > 0:
                    for j in range(interval):
                        iobw_r[ost_c][t_p + j] += round(read_value / 1024.0 * 4 / interval, 2)
                        iobw_w[ost_c][t_p + j] += round(write_value / 1024.0 * 4 / interval, 2)
                ost_p = ost_c
                read_p = read_c
                write_p = write_c
                t_p = t_c
            else:
                ost_p = ost_c
                read_p = read_c
                write_p = write_c
                t_p = t_c
        except Exception as e:
            print e
            continue
        
    for i in range(440):
        dict_r[str(i)] = iobw_r[i]
        dict_w[str(i)] = iobw_w[i]
    
    iobw = {}
    iobw['arr_xaxis'] = get_time_list(time_s, time_e)
    iobw['iobw_r'] = dict_r
    iobw['iobw_w'] = dict_w

    dte = time.time()
    print 'Dealing time : ' + str(round(dte - dts, 2)) + ' s.'

    print 'Begin caching dict...'
    cts = time.time()
    r.set('r', dict_r)
    cte = time.time()
    print 'Caching dict time : ' + str(round(cte - cts, 2)) + ' s.'
    return iobw

def redis_data():
    return r.get('data')

if __name__ == '__main__':
    start = time.time()
    query_ost(time_s, time_e)
    end = time.time()

    print 'PROGRAM RUNTIME : ' + str(round(end - start, 2)) + ' s'






















