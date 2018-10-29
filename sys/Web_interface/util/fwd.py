# -*- coding: utf-8 -*-
import datetime, elasticsearch1 as ES
from elasticsearch1 import helpers
from util import *

FWD_NUM = 145
ES_HOST = '20.0.8.87'

def search(time_s, time_e, fwd_host_list, index):
    time_start = time_s[:10] +'T' + time_s[11:] + '.000Z'
    time_end =time_e[:10] + 'T' + time_e[11:] + '.000Z'
    index_all = "logstash-" + index
    ES_SERVERS = [{'host' : ES_HOST, 'port': 9200}]
    es_client = ES.Elasticsearch(hosts = ES_SERVERS)

    match_query = []
    for i in xrange(len(fwd_host_list)):
        match_query.append({"match":{"host": fwd_host_list[i]}})
    es_search_options = {"query":{"bool": {"must":[{"range":{"@timestamp":{"gt":time_start,"le":time_end}}}]}}}

    es_result = helpers.scan(
            client = es_client,
            query = es_search_options,
            scroll = '3m',
            index = index_all,
            doc_type = 'redis-input',
            timeout = '1m'
            )

    final_result_host = []
    final_result_message = []
    final_result_time = []
    
    rlen = 0
    for item in es_result:
        rlen += 1
        final_result_message.append(str(item['_source']['message']))                                                            
        final_result_host.append(str(item['_source']['host']))
        final_result_time.append(str(item['_source']['@timestamp']))

    return final_result_message,final_result_time, final_result_host

def query_fwd(time_s, time_e):
    dict_r = {}
    dict_w = {}
    dict_hit = {}
    dict_miss = {}
    dict_discard = {}

    stime = datetime.datetime.strptime(time_s, '%Y-%m-%d %H:%M:%S') # the query start time
    etime = datetime.datetime.strptime(time_e, '%Y-%m-%d %H:%M:%S') # the query end time
    arr_length = (etime - stime).seconds

    iobw_r = [([0] * arr_length) for i in range(FWD_NUM)] 
    iobw_w = [([0] * arr_length) for i in range(FWD_NUM)] 
    cache_hit_list = [([0] * arr_length) for i in range(FWD_NUM)] 
    cache_miss_list = [([0] * arr_length) for i in range(FWD_NUM)] 
    cache_discard_list = [([0] * arr_length) for i in range(FWD_NUM)] 
    
    fwd_host_list = []
    for i in range(17,144): #gio
        fwd_host_list.append('20.0.2.'+str(i))
    #for i in range(1,90): #bio
        #fwd_host_list.append('20.0.208.'+str(i))
    index_list = get_index(time_s, time_e)

    res_msg = []
    res_time = []
    res_host = []
    result = []
    try:
        query_start = time.time()
        for idx in range(len(index_list)):
            msg_temp, time_temp, host_temp = search(time_s, time_e, fwd_host_list, index_list[idx])
            res_msg += msg_temp
            res_time += time_temp
            res_host += host_temp
        query_end = time.time()
        print 'Query finished, time spent : ' + str(round(query_end - query_start, 2)) + ' s'
    except Exception as e:
        print e
    
    for i in range(len(res_msg)):
        temp_str = res_host[i].split('.')[3] + ' ' + res_msg[i] + ' ' + res_time[i] # host + message + timestamp
        result.append(temp_str.replace(',', '').replace('[', '').replace(']', '').split(' '))

    result.sort(key=lambda x:(int(x[0]), x[1], x[-1]))

    t0 = stime # the query start time
    fwdid_p = int(result[0][0])
    ost_p = int(result[0][1], 16)
    try:
        t_p = (datetime.datetime.strptime(str(result[0][-1])[:10] + ' ' + str(result[0][-1])[11:-5], '%Y-%m-%d %H:%M:%S') - t0).seconds
    except Exception as e:
        print 'Bad time format'
    read_p = 0
    write_p = 0
    for i in range(2, len(result[0]) - 1, 3):
        read_p += int(result[0][i]) * int(result[0][i+1])
        write_p += int(result[0][i]) * int(result[0][i+2])

    cache_fwdid_p = 0
    cache_t_p = 0
    cache_hit_p = 0
    cache_miss_p =0
    cache_discard_p = 0
    for item in range(0, len(result)):
        record = result[item]
        if 'cache_hit' in record:
            print record
            cache_fwdid_p = int(record[0])
            cache_t_p = (datetime.datetime.strptime(str(record[-1])[:10] + ' ' + str(record[-1])[11:-5], '%Y-%m-%d %H:%M:%S') - t0).seconds
            cache_hit_p = int(record[2])
            cache_miss_p = int(record[4])
            cache_discard_p = int(record[6])
            break

    print 'cfid0 : ' + str(cache_fwdid_p) + ' ctp0 : ' + str(cache_t_p) + ' hit0 : ' + str(cache_hit_p) + ' miss0 : ' + str(cache_miss_p) + ' discard0 : ' + str(cache_discard_p)
################ BEGIN TO DEAL DATA ################    
    cache_count = 0
    for item in range(1, len(result)):
        record =  result[item] 
        fwdid_c = int(record[0])
        t_c = (datetime.datetime.strptime(str(record[-1])[:10] + ' ' + str(record[-1])[11:-5], '%Y-%m-%d %H:%M:%S') - t0).seconds

        if 'cache_hit' in record:
            cache_count += 1
            if cache_count == 1:
                continue
            else:
                cache_fwdid_c = fwdid_c
                cache_t_c = (datetime.datetime.strptime(str(record[-1])[:10] + ' ' + str(record[-1])[11:-5], '%Y-%m-%d %H:%M:%S') - t0).seconds
                cache_hit_c = int(record[2])
                cache_miss_c = int(record[4])
                cache_discard_c = int(record[6])
                interval = cache_t_c - cache_t_p
                #print 'cfid : ' + str(cache_fwdid_c) + ' ctp : ' + str(cache_t_c) + ' hit : ' + str(cache_hit_c) + ' miss : ' + str(cache_miss_c) + ' discard : ' + str(cache_discard_c)
                if cache_fwdid_c == cache_fwdid_p:
                    if interval > 0:
                        hit_value = cache_hit_c - cache_hit_p
                        miss_value = cache_miss_c - cache_miss_p
                        discard_value = cache_discard_c - cache_discard_p
                        for j in range(interval):
                            cache_hit_list[cache_fwdid_c][cache_t_p + j] += round(hit_value / 1024.0 * 4 /interval, 2)
                            cache_miss_list[cache_fwdid_c][cache_t_p + j] += round(miss_value / 1024.0 * 4 /interval, 2)
                            cache_discard_list[cache_fwdid_c][cache_t_p + j] += round(discard_value / 1024.0 * 4 /interval, 2)
                        
                        cache_fwdid_p = cache_fwdid_c
                        cache_t_p = cache_t_c
                        cache_hit_p = cache_hit_c
                        cache_miss_p = cache_miss_c
                        cache_discard_p = cache_discard_c
                else:
                    cache_fwdid_p = cache_fwdid_c
                    cache_t_p = cache_t_c
                    cache_hit_p = cache_hit_c
                    cache_miss_p = cache_miss_c
                    cache_discard_p = cache_discard_c
            continue

        try:
            read_c = 0
            write_c = 0
            for i in range(2, len(record) - 1, 3):
                read_c += int(record[i]) * int(record[i + 1])
                write_c += int(record[i]) * int(record[i + 2])
            ost_c = int(record[1], 16)
            #print 't_c : ' + str(t_c) + ' fwdid_c : ' + str(fwdid_c) + ' read : ' + str(read_c) + ' write : ' + str(write_c) 

            if fwdid_c == fwdid_p and ost_c == ost_p:
                interval = t_c - t_p
                read_value = int(read_c) - int(read_p)
                write_value = int(write_c) - int(write_p)
                if interval > 0:
                    for j in range(interval):
                        iobw_r[fwdid_c][t_p + j] += round(read_value * 4.0 / 1024.0 / interval, 2)
                        iobw_w[fwdid_c][t_p + j] += round(write_value * 4.0 / 1024 / interval, 2)
                fwdid_p = fwdid_c
                ost_p = ost_c
                read_p = read_c
                write_p = write_c
                t_p = t_c

            else:
                fwdid_p = fwdid_c
                ost_p = ost_c
                read_p = read_c 
                write_p = write_c
                t_p = t_c
        except Exception as e:
            print e
            continue
        
    for i in range(FWD_NUM):
        dict_r[str(i)] = iobw_r[i]
        dict_w[str(i)] = iobw_w[i]
        dict_hit[str(i)] = cache_hit_list[i]
        dict_miss[str(i)] = cache_miss_list[i]
        dict_discard[str(i)] = cache_discard_list[i]
    
    fwd_data = {}
    fwd_data['arr_xaxis'] = get_time_list(time_s, time_e)
    fwd_data['iobw_r'] = dict_r
    fwd_data['iobw_w'] = dict_w
    fwd_data['cache_hit'] = dict_hit
    fwd_data['cache_miss'] = dict_miss
    fwd_data['cache_discard'] = dict_discard
    return fwd_data




if __name__ == '__main__':
    time_s = '2018-07-23 08:00:00'
    time_e = '2018-07-23 08:00:50'

    query_fwd(time_s, time_e)
