from OST_each_all import search
from OST_each_all import search_le
from OST_each_all import search_gt
from elasticsearch1 import helpers
import sys, datetime, csv, time, random
import elasticsearch1 as ES
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('../')
from util import *

mbyte = 1048576.0 # 1024 * 1024
ost_num = 440
height = 300
time_s = '2018-02-02 10:00:00'
time_e = '2018-02-02 10:00:10'

def search(time_s, time_e, host, index, host_t):
    time_start = time_s[:10] + 'T' + time_s[11:] + '.000Z'
    time_end = time_e[:10] + 'T' + time_e[11:] + '.000Z'
    host_all = '20.0.8.' + str(host_t)
    index_all = "logstash-" + index
    ES_SERVERS = [{'host' : host_all, 'port': 9200}]

    es_client = ES.Elasticsearch(hosts = ES_SERVERS)

    match_query = []
    for i in xrange(len(host)):
        match_query.append({"match":{"host": host[i]}})
    es_search_options = {"query":{"bool":{"must":[{"range":{"@timestamp":{"gt":time_start,"lt":time_end}}}]}}}
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
    index = 0
    for item in es_result:
        index += 1
        final_result_message.append(str(item['_source']['message']))                                                            
        final_result_time.append(str(item['_source']['@timestamp']))

    return final_result_message, final_result_time

def get_time_interval(time_s, time_e):
    s = datetime.datetime.strptime(str(time_s), '%Y-%m-%d %H:%M:%S')
    e = datetime.datetime.strptime(str(time_e), '%Y-%m-%d %H:%M:%S')

    return (e - s).seconds

def query_ost(time_s, time_e):
    result_dict = {}
    result = []

    arr_length = get_time_interval(time_s, time_e)
    iobw_r = [([0] * arr_length) for i in range(ost_num)] 
    iobw_w = [([0] * arr_length) for i in range(ost_num)] 
    
    index = get_index(time_s)
    hostlist = []
    host_t = 90
    try:
        query_start = time.time()
        query_result = search(time_s, time_e, hostlist, index, host_t)
        query_end = time.time()
        print 'Query finished, time spent : ' + str(round(query_end - query_start)) + ' s'
    except Exception as e:
        print e
    
    for i in xrange(len(query_result[0])):
        result.append(query_result[0][i] + ' ' + query_result[1][i]) # message + timestamp
    result.sort()
   
    t0 = datetime.datetime.strptime(time_s, '%Y-%m-%d %H:%M:%S') # the query start time
    r1 = result[0].replace(',','').replace('[', '').replace(']', '').split(' ') # the first record in the query result
    ost_p = int(r1[0], 16)
    time_p = datetime.datetime.strptime(str(r1[-1])[:10] + ' ' + str(r1[-1])[11:-5], '%Y-%m-%d %H:%M:%S')
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
        
    print "start write CSV..."
    count = 0
    oscid = []
    csvfile = file('./OSTCSV' + index + '.csv','wb')
    writer = csv.writer(csvfile)
    for i in range(arr_length):
        row_value = []
        for j in range(440):
            row_value.append(iobw_r[j][i])
            row_value.append(iobw_w[j][i])
        writer.writerow(row_value)
    csvfile.close()

    return iobw_r, iobw_w
    print "start plot..."
    ax=plt.gca()
    for i in range(440):
        if np.array(iobw_r[i]).sum()>0 or np.array(iobw_w[i]).sum()>0:
            ax.plot(np.array(iobw_r[i]) + height * count, 'r', label = 'Read')
            ax.plot(np.array(iobw_w[i]) + height * count, 'b', label = 'Write')
            oscid.append(str(int(hex(i), 16)))
            count += 1
            if count >= 20:
                ax.set_yticks(np.linspace(0, count * height, count + 1))
                ax.set_yticklabels(oscid)
                plt.ylabel('Forwarding ID')
                plt.xlabel('Time(s)')
                plt.show()
                ax = plt.gca()
                count = 0
                oscid = []

    if count > 0:
        ax.set_yticks(np.linspace(0, count * height, count + 1))
        ax.set_yticklabels(oscid)
        plt.ylabel('Forwarding ID')
        plt.xlabel('Time(s)')
        plt.show()

if __name__ == '__main__':
    start = time.time()
    query_ost(time_s, time_e)
    end = time.time()

    print 'PROGRAM RUNTIME : ' + str(round(end - start, 2)) + ' s'






















