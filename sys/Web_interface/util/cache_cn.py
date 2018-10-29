import sys, json, csv, datetime, random, numpy as np, redis, elasticsearch1 as ES
from elasticsearch1 import helpers
from db_util import *
from util import *

IP_GROUP = 200
MB = 1024 * 1024
ES_HOST = '20.0.8.' + str(random.randint(10, 60)) #[10, 60]
CN_NUM = 40960
JOBID = 43108284
STIME = '2018-07-30 08:41:34'
ETIME = '2018-07-30 08:58:59'

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
redis_cli = redis.Redis(connection_pool = pool)

def search(es_stime, es_etime, ip_list, index):
    index_all = 'logstash-' + index
    es_servers = [{'host':ES_HOST, 'port':9200}]
    
    match_query = []
    for i in range(len(ip_list)):
        match_query.append({'match':{'host':ip_list[i]}})

    es_search_options = {'query':{'bool':{
                                'must':[{'bool':{'should':[match_query]}},{'range':{'@timestamp':{'gt':es_stime, 'lt':es_etime}}}],
                                'should':[{'match':{'message':'OPEN'}},{'match':{'message':'RELEASE'}},
                                          {'match':{'message':'READ'}},{'match':{'message':'WRITE'}}]
                        }}}
    es_client = ES.Elasticsearch(hosts = es_servers)
    es_result = helpers.scan(client = es_client, query = es_search_options, scroll = '5m', index = index_all, doc_type = 'redis-input', timeout = '1m')

    res_message = []
    for item in es_result:
        res_message.append((item['_source']['@timestamp'][0:10] + ' ' + item['_source']['@timestamp'][11:19] + ' ' +  item['_source']['message'][24:] + ' ' + item['_source']['host']).split(' '))
    return res_message

def cache_cn(jobid, stime, etime):
    time_utc = datetime.timedelta(hours = 8)
    query_stime = datetime.datetime.strptime(stime, "%Y-%m-%d %H:%M:%S") - time_utc
    query_etime = datetime.datetime.strptime(etime, "%Y-%m-%d %H:%M:%S") - time_utc - datetime.timedelta(seconds=1)
    es_stime = str(query_stime)[:10] + 'T' + str(query_stime)[11:] + '.000z'
    es_etime = str(query_etime)[:10] + 'T' + str(query_etime)[11:] + '.000z'
    min_time = datetime_to_sec(str(query_stime))
    max_time = datetime_to_sec(str(query_etime))
    
    #print query_stime
    #print query_etime
    #print min_time
    #print max_time
    #exit()

    index_list = get_index(es_stime, es_etime)    
    #ip_list = get_total_ip_list()
    ip_list = get_job_node_ip_list(jobid)
    node_list = get_job_node_list(jobid)
    arr_length = max_time - min_time + 1

    iobw_r = [([0] * arr_length) for i in range(CN_NUM)]
    iobw_w = [([0] * arr_length) for i in range(CN_NUM)]
    iops_r = [([0] * arr_length) for i in range(CN_NUM)]
    iops_w = [([0] * arr_length) for i in range(CN_NUM)]
    file_open = [([0] * arr_length) for i in range(CN_NUM)]
    file_close = [([0] * arr_length) for i in range(CN_NUM)]

    ip_iteration = len(ip_list) / IP_GROUP
    ip_remainder = len(ip_list) % IP_GROUP
    
    res_message = []
    try:
        for idx in xrange(len(index_list)):
            if ip_iteration > 0:
                for ip_idx in xrange(ip_iteration):
                    try:
                        message_temp = search(es_stime, es_etime, ip_list[(ip_idx * IP_GROUP):(ip_idx * IP_GROUP + IP_GROUP)], index_list[idx])
                        res_message += message_temp
                    except Exception as e:
                        print e
            if ip_remainder > 0:
                message_temp = search(es_stime, es_etime, ip_list[-ip_remainder:], index_list[idx])
                res_message += message_temp
    except Exception as e:
        print e

    s = time.time()
    res_message.sort(key = lambda x:(x[-1], (x[0] + x[1])))
    e = time.time()
    print 'Sorting Time : ' + str(round(e - s, 2)) + ' s.'
    ip_p = res_message[0][-1]

    cn_id = get_cnode_id(ip_p)
    for msg in res_message:
        ip_c = msg[-1]
        tmp = []
        if ip_p != ip_c:
            cn_id = get_cnode_id(ip_c)
        
        time_c = msg[0] + ' ' + msg[1]
        try:
            index = int(time.mktime(time.strptime(time_c, "%Y-%m-%d %H:%M:%S"))) - min_time 
        except Exception as e:
            print e
            continue

        if 'READ' in msg:
            try:
                if 'offset' in msg:
                    read_size = int(msg[5].split('=')[1])
                    read_op = int(msg[7].split('=')[1])
                    #iobw_r[cn_id][index] += round(read_size * read_op / MB, 2)
                    iobw_r[cn_id][index] += read_size * read_op * 1.0 / MB
                    iops_r[cn_id] += read_op
                else:
                    read_size = int(msg[4].split('=')[1])
                    read_op = int(msg[5].split('=')[1])
                    #iobw_r[cn_id][index] += round(read_size / MB, 2)
                    iobw_r[cn_id][index] += read_size * 1.0 / MB
                    iops_r[cn_id][index] += read_op
            except Exception as e:
                print e
                continue
        elif 'WRITE' in msg:
            try:
                if 'offset' in msg:
                    write_size = int(msg[5].split('=')[1])
                    write_op = int(msg[7].split('=')[1])
                    #iobw_w[cn_id][index] += round(write_size * write_op / MB, 2)
                    iobw_w[cn_id][index] += write_size * write_op * 1.0 / MB
                    iops_w[cn_id][index] += write_op
                else:
                    write_size = int(msg[4].split('=')[1])
                    write_op = int(msg[5].split('=')[1])
                    #iobw_w[cn_id][index] += round(write_size / MB, 2)
                    iobw_w[cn_id][index] += write_size * 1.0 / MB
                    iops_w[cn_id][index] += write_op
            except Exception as e:
                print e
                continue
        elif 'OPEN' in msg:
            try:
                file_open[cn_id][index] += 1
            except Exception as e:
                print 'open'
                continue
        elif 'RELEASE' in msg:
            try:
                file_close[cn_id][index] += 1
            except Exception as e:
                print 'close'
                continue
        ip_p = ip_c

    #s0 = time.time()
    #for cn in range(0, 10):
    #    tmp_res = []
    #    for i in range(0, arr_length):
    #        tmp_res.append((iobw_r[i], iobw_w[i], iops_r[i], iops_w[i], file_open[i], file_close[i]))    
    #    redis_cli.rpush('0801-0-c' + str(cn), *tmp_res)
    #e0 = time.time()
    #print 'Method 1 Time : ' + str(round(e0 - s0, 2)) + ' s.'
    #exit()
    cs = time.time()
    prefix = 'test-'
    for cn in node_list:
        redis_cli.rpush(prefix + str(cn), *iobw_r[cn]) 
        redis_cli.rpush(prefix + str(cn), *iobw_w[cn]) 
        redis_cli.rpush(prefix + str(cn), *iops_r[cn]) 
        redis_cli.rpush(prefix + str(cn), *iops_w[cn]) 
        redis_cli.rpush(prefix + str(cn), *file_open[cn]) 
        redis_cli.rpush(prefix + str(cn), *file_close[cn]) 

        #redis_cli.rpush('0714-14-c-br-' + str(cn), *iobw_r[cn]) 
        #redis_cli.rpush('0714-14-c-bw-' + str(cn), *iobw_w[cn]) 
        #redis_cli.rpush('0714-14-c-pr-' + str(cn), *iops_r[cn]) 
        #redis_cli.rpush('0714-14-c-pw-' + str(cn), *iops_w[cn]) 
        #redis_cli.rpush('0714-14-c-fo-' + str(cn), *file_open[cn]) 
        #redis_cli.rpush('0714-14-c-fc-' + str(cn), *file_close[cn]) 
    ce = time.time()
    print 'Caching Time : ' + str(round(ce -cs, 2)) + ' s.'

def get_total_ip_list():
    total_ip_list = []
    for cn_id in range(40960):
        total_ip_list.append(get_cnode_ip(cn_id))
    
    return total_ip_list

if __name__=='__main__':
    s = time.time()
    print 'Beging caching, time from ' + STIME + ' to ' + STIME
    cache_cn(JOBID, STIME, ETIME)
    e = time.time()
    print 'Program Running Time : ' + str(round(e -s, 2)) + ' s.' 
