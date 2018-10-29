import sys, json, csv, datetime
import numpy as np
from pyes import *
from db_util import *
from util import *
es_address = '20.0.8.10::9200'
compression = 5000

# get the query data
# data type 0:iobw  1:iops 2:file open/close
# r:read w:write
def query_data(es_stime, es_etime, min_time, max_time, iplist, data_type):
    arr_length = max_time - min_time + 1
    print arr_length
    iobw_r = np.array([0.0 for i in range(arr_length)])
    iobw_w = np.array([0.0 for i in range(arr_length)])
    iops_r = np.array([0.0 for i in range(arr_length)])
    iops_w = np.array([0.0 for i in range(arr_length)])
    file_open = np.array([0.0 for i in range(arr_length)])
    file_close = np.array([0.0 for i in range(arr_length)])

    es_conn = ES(es_address)
    q0 = RangeQuery(qrange = ESRange('@timestamp', from_value = es_stime, to_value = es_etime))
    q1 = ''
    q2 = ''
    q3 = MatchQuery('message', 'READ')
    q4 = MatchQuery('message', 'WRITE')
    q5 = MatchQuery('message', 'OPEN')
    q6 = MatchQuery('message', 'RELEASE')
    q7 = BoolQuery(should = [q3, q4, q5, q6])
    
    ip_count = 0
    for i in range(len(iplist)):
        ip_count += 1
        if ip_count == 1:
            q1 = MatchQuery('host', iplist[i])
        else:
            q2 = MatchQuery('host', iplist[i])
            q1 = BoolQuery(should = [q1, q2])
        if ip_count >= 10:
            ip_count = 0
            query = BoolQuery(must = [q1, q0, q7])
            search = Search(query, fields = ['host'])
            results = es_conn.search(search)
            iterations = len(results) / compression + 1

            for k in range(0, iterations):
                search = Search(query, fields = ['message', 'host'], size = compression, start = k * compression)
                results = es_conn.search(search)
                for r in results:
                    record = str(remove_unicode(str(r))).split()
                    c_time = (record[1][2:] + ' ' + record[2])[1:-1]
                    index = datetime_to_sec(c_time) - min_time + 1
                    operation = record[4]
                    if operation == 'READ':
                        try:
                            read_size = int(record[5].split('=')[1])
                            read_op = int(record[6].split('=')[1])
                            iobw_r[index] += read_size / 1024.0
                            iops_r[index] += read_op
                        except Exception as e:
                            print e
                    elif operation == 'WRITE':
                        try:
                            write_size = int(record[5].split('=')[1])
                            write_op = int(record[6].split('=')[1])
                            iobw_w[index] += write_size / 1024.0
                            iops_w[index] += write_op
                        except Exception as e:
                            print 'write'
                            print e
                    elif operation == 'OPEN':
                        try:
                            file_open[index] += 1
                        except Exception as e:
                            print 'open'
                    elif operation == 'RELEASE':
                        try:
                            file_close[index] += 1
                        except Exception as e:
                            print 'close'

    if ip_count > 0:
        query = BoolQuery(must = [q1,q0,q7])
        search = Search(query, fields = ['host'])
        results = es_conn.search(search)
        iterations = len(results) / compression + 1

        for k in range(0, iterations):
            search = Search(query, fields = ['message', 'host'], size = compression, start = k * compression)
            results = es_conn.search(search)
            for r in results:
                record = str(remove_unicode(str(r))).split()
                c_time = (record[1][2:] + ' ' + record[2])[1:-1]
                index = datetime_to_sec(c_time) - min_time + 1
                print index
                operation = record[4]
                if operation == 'READ':
                    try:
                        read_size = int(record[5].split('=')[1])
                        read_op = int(record[6].split('=')[1])
                        iobw_r[index] += read_size / 1024.0
                        iops_r[index] += read_op
                    except Exception as e:
                        print e
                elif operation == 'WRITE':
                    try:
                        write_size = int(record[5].split('=')[1])
                        write_op = int(record[6].split('=')[1])
                        iobw_w[index] += write_size / 1024.0
                        iops_w[index] += write_op
                    except Exception as e:
                        print e
                elif operation == 'OPEN':
                    try:
                        file_open[index] += 1
                    except Exception as e:
                        print e
                elif operation == 'RELEASE':
                    try:
                        file_close[index] += 1
                    except Exception as e:
                        print e

    if data_type == 0:
        return iobw_r, iobw_w
    if data_type == 1:
        return iops_r, iops_w
    if data_type == 2:
        return file_open, file_close
        


if __name__=='__main__':
    jobid = sys.argv[5]
    start_time = sys.argv[1] + ' ' + sys.argv[2] 
    end_time = sys.argv[3] + ' ' + sys.argv[4]

    es_stime, es_etime, min_time, max_time = get_query_para(jobid, start_time, end_time)
    ip_list = get_job_node_ip_list(jobid)
    
    query_start = time.time()
    resultr, resultw = query_data(es_stime, es_etime, min_time, max_time, ip_list, 0)
    query_end = time.time()
    print 'QUERY TIME : ' + str(round(query_end - query_end, 2)) + ' s'
    total_write=0.0
    total_read=0.0
    data = []
    for  i in range(len(resultr)):
        resultr[i]/=1024.0
        resultw[i]/=1024.0
        total_write+=resultw[i]
        total_read+=resultr[i]
    for line in xrange(len(resultr)):
        data.append((str(resultr[line]),str(resultw[line])))

    print "Total read bandwidth is " + str(total_read) + " MB/S"
    print "Total write bandwidth is " + str(total_write) + "MB/S"
