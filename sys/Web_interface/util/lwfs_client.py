import sys, json, csv, datetime, random, numpy as np, redis
import elasticsearch1 as ES
from elasticsearch1 import helpers
from db_util import *
from util import *

IP_GROUP = 200
MB = 1024 * 1024
ES_HOST = '20.0.8.' + str(random.randint(10, 60)) #[10, 60]
REDIS_HOST = '20.0.2.203'
JOBID = 42967351

pool = redis.ConnectionPool(host=REDIS_HOST, port=6379, decode_responses=True)
r = redis.Redis(connection_pool = pool)

def search(es_stime, es_etime, ost_host, index):
    index_all = 'logstash-' + index
    es_servers = [{'host':ES_HOST, 'port':9200}]
    
    match_query = []
    for i in range(len(ost_host)):
        match_query.append({'match':{'host':ost_host[i]}})
    #match_query.append({'match':{'host':'172.35.32.6'}})

    es_search_options = {'query':{'bool':{
                                'must':[{'bool':{'should':[match_query]}},{'range':{'@timestamp':{'gt':es_stime, 'lt':es_etime}}}],
                                'should':[{'match':{'message':'OPEN'}},{'match':{'message':'RELEASE'}},
                                          {'match':{'message':'READ'}},{'match':{'message':'WRITE'}}]
                        }}}
    es_client = ES.Elasticsearch(hosts = es_servers)
    es_result = helpers.scan(client = es_client, query = es_search_options, scroll = '5m', index = index_all, doc_type = 'redis-input', timeout = '1m')

    res_message = []
    #res_host = []
    for item in es_result:
        res_message.append(str(item['_source']['message']))
        #res_host.append(str(item['_source']['host']))

    #print res_host
    return res_message

def get_search_result(jobid, start_time, end_time):
    es_stime, es_etime, min_time, max_time = get_query_para(jobid, start_time, end_time)
    ip_list = get_job_node_ip_list(jobid)
    index_list = get_index(es_stime, es_etime)    

    arr_length = max_time - min_time + 1
    iobw_r = [0 for i in range(arr_length)]
    iobw_w = [0.0 for i in range(arr_length)]
    iops_r = [0 for i in range(arr_length)]
    iops_w = [0.0 for i in range(arr_length)]
    file_open = [0.0 for i in range(arr_length)]
    file_close = [0.0 for i in range(arr_length)]

    ip_iteration = len(ip_list) / IP_GROUP
    ip_remainder = len(ip_list) % IP_GROUP
    
    res_message = []
    try:
        qs = time.time()
        for idx in xrange(len(index_list)):
            #print 'Searching index : ' + index_list[idx]
            if ip_iteration > 0:
                for ip_idx in xrange(ip_iteration):
                    #print 'Searching ip group : ' + str(ip_idx)
                    try:
                        message_temp = search(es_stime, es_etime, ip_list[(ip_idx * IP_GROUP):(ip_idx * IP_GROUP + IP_GROUP)], index_list[idx])
                        res_message += message_temp
                    except Exception as e:
                        print e
                        continue
            if ip_remainder > 0:
                message_temp = search(es_stime, es_etime, ip_list[-ip_remainder:], index_list[idx])
                res_message += message_temp
        qe = time.time()
        print '[Cache Miss] Getting Data Time : ' + str(qe - qs) + ' s.'
    except Exception as e:
        print e


    ds = time.time()
    res_len = 0
    #res_len = len(res_message)
    for msg in res_message:
        res_len += 1
        msg_arr = msg.split(' ')
        c_time = msg[1:20]
        try:
            index = datetime_to_sec(c_time) - min_time 
        except Exception as e:
            #print e
            continue

        if 'READ' in msg:
            try:
                if 'offset' in msg:
                    read_size = int(msg_arr[5].split('=')[1])
                    read_op = int(msg_arr[7].split('=')[1])
                    iobw_r[index] += round(read_size * read_op / MB, 2)
                    #iobw_r[index] += read_size * read_op * 1.0 / MB
                    iops_r[index] += read_op
                else:
                    read_size = int(msg_arr[4].split('=')[1])
                    read_op = int(msg_arr[5].split('=')[1])
                    iobw_r[index] += round(read_size / MB, 2)
                    #iobw_r[index] += read_size * 1.0 / MB
                    iops_r[index] += read_op
            except Exception as e:
                #print e
                continue
        elif 'WRITE' in msg:
            try:
                if 'offset' in msg:
                    write_size = int(msg_arr[5].split('=')[1])
                    write_op = int(msg_arr[7].split('=')[1])
                    iobw_w[index] += round(write_size * write_op / MB, 2)
                    #iobw_w[index] += write_size * write_op * 1.0 / MB
                    iops_w[index] += write_op
                else:
                    write_size = int(msg_arr[4].split('=')[1])
                    write_op = int(msg_arr[5].split('=')[1])
                    iobw_w[index] += round(write_size / MB, 2)
                    #iobw_w[index] += write_size * 1.0 / MB
                    iops_w[index] += write_op
            except Exception as e:
                #print e
                continue
        elif 'OPEN' in msg:
            try:
                file_open[index] += 1
            except Exception as e:
                #print 'open'
                continue
        elif 'RELEASE' in msg:
            try:
                file_close[index] += 1
            except Exception as e:
                #print 'close'
                continue

    print 'ES Result Length : ' + str(res_len)
    data = {}
    data['iobw_r'] = iobw_r
    data['iobw_w'] = iobw_w
    data['iops_r'] = iops_r
    data['iops_w'] = iops_w
    data['file_open'] = file_open
    data['file_close'] = file_close
    if start_time == '':
        time_utc = datetime.timedelta(hours=8)
        start_time = str(datetime.datetime.strptime(es_stime[0:10] + ' ' + es_stime[11:19], "%Y-%m-%d %H:%M:%S") + time_utc)
        end_time = str(datetime.datetime.strptime(es_etime[0:10] + ' ' + es_etime[11:19], "%Y-%m-%d %H:%M:%S") + time_utc)
        data['arr_xaxis'] = get_time_list(start_time, end_time)
    else:
        data['arr_xaxis'] = get_time_list(start_time, end_time)

    de = time.time()
    print '[Cache Miss] Dealing Data Time : ' + str(round(de - ds, 2)) + ' s.'

    return data

def get_cache(jobid, start_time='', end_time=''):
    s1 = time.time()
    node_list = get_job_node_list(jobid)
    es_stime, es_etime, min_time, max_time = get_query_para(jobid, start_time, end_time)
    arr_length = max_time - min_time + 1
    m = time.time()
    iobw_r = [0 for i in range(arr_length)]
    iobw_w = [0.0 for i in range(arr_length)]
    iops_r = [0 for i in range(arr_length)]
    iops_w = [0.0 for i in range(arr_length)]
    file_open = [0.0 for i in range(arr_length)]
    file_close = [0.0 for i in range(arr_length)]
    e1 = time.time()
    print 'Cache prepare time 1 : ' + str(round(m - s1, 2)) + ' s.'
    print 'Cache prepare time 2 : ' + str(round(e1 - m, 2)) + ' s.'

    prefix = str(jobid) + '-'
    s = time.time()
    for node in node_list:
        br = r.get(prefix + str(node)).split(',')
        #bw = r.get(prefix + str(int(node))).split(',')
        #br = r.get(prefix + str(int(node))).split(',')
        #br = r.get(prefix + str(int(node))).split(',')
        #br = r.get(prefix + str(int(node))).split(',')
        #br = r.get(prefix + str(int(node))).split(',')
        
        for i in range(arr_length):
            iobw_r[i] += float(br[i])
            #iobw_w[i] += float(bw[i])
            #iops_r[i] += float(pr[i])
            #iops_w[i] += float(pw[i])
            #file_open[i] += float(fo[i])
            #file_close[i] += float(fc[i])
    e = time.time()
    print 'Get data time : ' + str(round(e - s, 2)) + ' s.'

    s2 = time.time()
    data = {}
    data['iobw_r'] = iobw_r
    data['iobw_w'] = iobw_w
    data['iops_r'] = iops_r
    data['iops_w'] = iops_w
    data['file_open'] = file_open
    data['file_close'] = file_close
    if start_time == '':
        time_utc = datetime.timedelta(hours=8)
        start_time = str(datetime.datetime.strptime(es_stime[0:10] + ' ' + es_stime[11:19], "%Y-%m-%d %H:%M:%S") + time_utc)
        end_time = str(datetime.datetime.strptime(es_etime[0:10] + ' ' + es_etime[11:19], "%Y-%m-%d %H:%M:%S") + time_utc)
        data['arr_xaxis'] = get_time_list(start_time, end_time)
    else:
        data['arr_xaxis'] = get_time_list(start_time, end_time)
    e2 = time.time()
    print 'Cache post processing  time : ' + str(round(e2 -s2, 2)) + ' s.'

    return data

if __name__=='__main__':
    print get_cnode_ip(36101)
    #nodes = get_job_node_list(43087233)
    #print len(nodes)
    #jobid = sys.argv[5]
    #start_time = sys.argv[1] + ' ' + sys.argv[2] 
    #end_time = sys.argv[3] + ' ' + sys.argv[4]
    
    #get_search_result(jobid, start_time, end_time)
