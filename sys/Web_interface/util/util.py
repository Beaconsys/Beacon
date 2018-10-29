import datetime, time
from db_util import *

# remove character 'u' before a unicode string like u'string'
def remove_unicode(raw_string):
    new_string = raw_string.replace("u","")
    return new_string

# get the compute node's IP address
def get_cnode_ip(cnode_id):
    a = '172'
    b = int(cnode_id) // 1024
    c = (int(cnode_id) - b * 1024) // 8
    d = int(cnode_id) - b * 1024 - c * 8 + 1
    cnode_ip = str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d)
    
    return cnode_ip

def get_cnode_id(cnode_ip):
    arr = cnode_ip.split('.')
    cnode_id = int(arr[1]) * 1024 + int(arr[2]) * 8 + int(arr[3]) - 1

    return cnode_id


# get the compute node list of one job
def get_job_node_list(jobid):
    node_list = []
    node_info = get_job_by_id(str(jobid))[8].split(',')
    for node in node_info:
        nodes = node.split('-')
        if len(nodes) == 1:
            node_list.append(int(nodes[0]))
        else:
            for x in range(int(nodes[0]), int(nodes[1]) + 1):
                node_list.append(x)

    return node_list    

# get the IP address list of one job
def get_job_node_ip_list(jobid):
    ip_list = []
    node_list = get_job_node_list(jobid)
    for node in node_list:
        node_ip = get_cnode_ip(node)
        ip_list.append(node_ip)

    return ip_list

# transfer datetime to seconds format
def datetime_to_sec(xtime):
    sec = int(time.mktime(time.strptime(xtime, "%Y-%m-%d %H:%M:%S")))
    return sec

# transfer seconds to datetime format
def sec_to_datetime(sec):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec))

# get the ES query parameter, includes:
# 1: es_stime  the start time of the es query
# 2: es_etime  the end time of the es query
# 3: arr_length the length of the query result array
def get_query_para(jobid, stime = '', etime = ''):
    query_stime = ''
    query_etime = ''
    time_utc = datetime.timedelta(hours = 8)

    job_info = get_job_by_id(jobid)
    db_stime = job_info[3] # the job start-time recorded by the database
    db_etime = job_info[4] # the job end-time recorded by the database, this value maybe NONE

    if stime == '' and etime == '':
        query_stime = datetime.datetime.strptime(db_stime, "%Y-%m-%d %H:%M:%S")
        query_etime = datetime.datetime.strptime(db_etime, "%Y-%m-%d %H:%M:%S")
    else:
        if db_stime >= stime:
            query_stime = datetime.datetime.strptime(db_stime, "%Y-%m-%d %H:%M:%S")
        else:
            query_stime = datetime.datetime.strptime(stime, "%Y-%m-%d %H:%M:%S")

        if db_etime == 'None':
            print 'Sorry, but this job is still running.'
            query_etime = datetime.datetime.strptime(etime, "%Y-%m-%d %H:%M:%S")
        else:
            if db_etime <= etime:
                query_etime = datetime.datetime.strptime(db_etime, "%Y-%m-%d %H:%M:%S")
            else:
                query_etime = datetime.datetime.strptime(etime, "%Y-%m-%d %H:%M:%S")
    
    min_time = datetime_to_sec(str(query_stime))
    max_time = datetime_to_sec(str(query_etime))
    es_stime = str(query_stime - time_utc)[:10] + 'T' + str(query_stime - time_utc)[11:] + '.000z'
    es_etime = str(query_etime - time_utc)[:10] + 'T' + str(query_etime - time_utc)[11:] + '.000z'
    arr_length = max_time - min_time + 1 # the length of the query result array

    return es_stime, es_etime, min_time, max_time

# get gio and bio IP list
def get_host_ip_list():
    host = []
    # gio ip address
    for i in range(17, 144):
        if i <> 90:
            host.append('20.0.2.' + str(i))
    # bio ip address
    for i in range(1, 90):
        host.append('20.0.2.' + str(i))

    return host
    
# get the time interval between to date time, the unit is 1 second
def get_time_intervall(start_time, end_time):
    s = datetime.datetime.strptime(str(start_time), '%Y-%m-%d %H:%M:%S')
    e = datetime.datetime.strptime(str(end_time), '%Y-%m-%d %H:%M:%S')
    interval = int((e - s).seconds)

    return interval

# get the es index
def get_index(stime, etime):
    index_list = []
    begin_date = datetime.datetime.strptime(stime[0:10], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(etime[0:10], '%Y-%m-%d')
    while begin_date <= end_date:
        date_str = begin_date.strftime('%Y-%m-%d').split('-')
        index = date_str[0] + '.' + date_str[1] + '.' + date_str[2]
        index_list.append(index)
        begin_date += datetime.timedelta(days = 1)
    
    return index_list

# sort the dict according to the key
def sort_dict(target):
    keys = target.keys()
    keys.sort()
    return map(target.get, keys)

# convert hex to decimal
def hex_to_decimal(hex_num):
    return int(hex_num, 16)

def get_time_list(stime, etime):
    time_list = []
    UTC = datetime.timedelta(hours = 8)
    stime = datetime.datetime.strptime(stime, '%Y-%m-%d %H:%M:%S') + UTC
    etime = datetime.datetime.strptime(etime, '%Y-%m-%d %H:%M:%S') + UTC
    while stime <= etime:
        time_list.append(str(stime))
        stime += datetime.timedelta(seconds = 1)

    return time_list

if __name__=="__main__":
    #for i in range(1, 40961):
        #print get_cnode_ip(i)
    print get_cnode_ip(11550)
    #stime = '2017-01-01 00:00:00' 
    #etime = '2017-01-01 00:01:00'
    #time_list = get_time_list(stime, etime)
    #print time_list
    #print hex_to_decimal('00a2')
    #print get_index('2017-01-01 00:00:00')
    #print get_index('2017-10-22 00:00:00')

    #print get_time_interval('2017-01-01 10:00:00', '2017-01-01 10:00:10')
    #print get_host_ip_list()
    #a, b, c = get_query_interval(42793117, '2018-07-01 00:03:40', '2018-07-01 00:04:10') 
    #a, b, c = get_query_para(42793117) 
    #print a
    #print b
    #print c
    #print get_job_node_list(42793117)
    #print get_job_node_ip_list(8431283)
    
    #time_utc = datetime.timedelta(hours = 8)
    #print time_utc

    #sec = test("2017-01-02 00:00:00")
    #print test2(sec)
    #print calculate_cnodeIP(3000)
