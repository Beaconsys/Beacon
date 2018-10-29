import datetime
import time

from db_util import *

year_sec = 365*24*60*60
day_sec   = 24*60*60
hour_sec = 60*60
sec = 60

mon1_sec   = (31)*day_sec
mon2_sec   = (31+28)*day_sec
mon3_sec   = (31+28+31)*day_sec
mon4_sec   = (31+28+31+30)*day_sec
mon5_sec   = (31+28+31+30+31)*day_sec
mon6_sec   = (31+28+31+30+31+30)*day_sec
mon7_sec   = (31+28+31+30+31+30+31)*day_sec
mon8_sec   = (31+28+31+30+31+30+31+31)*day_sec
mon9_sec   = (31+28+31+30+31+30+31+31+30)*day_sec
mon10_sec = (31+28+31+30+31+30+31+31+30+31)*day_sec
mon11_sec = (31+28+31+30+31+30+31+31+30+31+30)*day_sec


def time_to_sec(day_time):
    x = time.strptime(day_time,'%Y-%m-%d %H:%M:%S')
    year_day_hour_min =  (x.tm_year) * year_sec + (x.tm_mday-1)*day_sec + x.tm_hour*hour_sec + x.tm_min*sec + x.tm_sec

    if x.tm_mon == 1:
        now_sec = year_day_hour_min
    elif x.tm_mon == 2:
        now_sec = mon1_sec + year_day_hour_min
    elif x.tm_mon == 3:
        now_sec = mon2_sec + year_day_hour_min
    elif x.tm_mon == 4:
        now_sec = mon3_sec + year_day_hour_min
    elif x.tm_mon == 5:
        now_sec = mon4_sec + year_day_hour_min
    elif x.tm_mon == 6:
        now_sec = mon5_sec + year_day_hour_min
    elif x.tm_mon == 7:
        now_sec = mon6_sec + year_day_hour_min
    elif x.tm_mon == 8:
        now_sec = mon7_sec + year_day_hour_min
    elif x.tm_mon == 9:
        now_sec = mon8_sec + year_day_hour_min
    elif x.tm_mon == 10:
        now_sec = mon9_sec + year_day_hour_min
    elif x.tm_mon == 11:
        now_sec = mon10_sec + year_day_hour_min
    else:
        now_sec = mon11_sec + year_day_hour_min
    return now_sec

def sec_to_time(secs):
    year=secs/year_sec
    res=secs-year*year_sec
    if res>=mon11_sec:
        month=12
        res=res-mon11_sec
    elif res>=mon10_sec:
        month=11
        res=res-mon10_sec
    elif res>=mon9_sec:
        month=10
        res=res-mon9_sec
    elif res>=mon8_sec:
        month=9
        res=res-mon8_sec
    elif res>=mon7_sec:
        month=8
        res=res-mon7_sec
    elif res>=mon6_sec:
        month=7
        res=res-mon6_sec
    elif res>=mon5_sec:
        month=6
        res=res-mon5_sec
    elif res>=mon4_sec:
        month=5
        res=res-mon4_sec
    elif res>=mon3_sec:
        month=4
        res=res-mon3_sec
    elif res>=mon2_sec:
        month=3
        res=res-mon2_sec
    elif res>=mon1_sec:
        month=2
        res=res-mon1_sec
    else:
        month=1
        res=res-0
    day=res/day_sec
    res=res-day*day_sec
    day=day+1
    hour=res/hour_sec
    res=res-hour*hour_sec
    mininute=res/sec
    second=res-mininute*sec
    str_year=str(year)
    if month<10:
        str_month='0'+str(month)
    else:
        str_month=str(month)
    if day<10:
        str_day='0'+str(day)
    else:
        str_day=str(day)
    if hour<10:
        str_hour='0'+str(hour)
    else:
        str_hour=str(hour)
    if mininute<10:
        str_min='0'+str(mininute)
    else:
        str_min=str(mininute)
    if second<10:
        str_sec='0'+str(second)
    else:
        str_sec=str(second)
    time=str_year+"-"+str_month+"-"+str_day+" "+str_hour+":"+str_min+":"+str_sec
    return time

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

# get 
def get_job_node_ip_list(jobid):
    ip_list = []
    node_list = get_job_node_list(jobid)
    for node in node_list:
        node_ip = get_cnode_ip(node)
        ip_list.append(node_ip)

    return ip_list

def test(xtime):
    sec = int(time.mktime(time.strptime(xtime, "%Y-%m-%d %H:%M:%S")))
    return sec

def test2(sec):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec))


if __name__=="__main__":
    #print get_job_node_list(42793117)
    #print get_job_node_ip_list(8431283)


    sec = test("2017-01-02 00:00:00")
    print test2(sec)
    #print calculate_cnodeIP(3000)
