import sys
import json
import csv
import datetime
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pyes import *
from pyes.aggs import TermsAgg
from pyes.queryset import  QuerySet
from db_util import *
from util import *
length=5000
es_conn=ES('20.0.8.10::9200')

read_active = []
write_active = []
def comput(es_stime,es_etime,ip):
    global min_time,read_active,write_active
    ip_count = 0
    q0 = RangeQuery(qrange=ESRange('@timestamp',from_value=es_stime,to_value=es_etime))
    q3 = MatchQuery("message","READ")
    q4 = MatchQuery("message","WRITE")
    q5 = BoolQuery(should=[q3,q4])
    for i in range(len(iplist)):
        ip_count += 1
        if ip_count==1:
            q1 = MatchQuery("host",iplist[i])
        else:
            q2=MatchQuery("host",iplist[i])
            q1=BoolQuery(should=[q1,q2])
        if ip_count>=30:
            ip_count = 0
            query = BoolQuery(must=[q1,q0,q5])
            search = Search(query,fields=["host"])
            results = es_conn.search(search)
            iterations = len(results)/length + 1

            for k in range(0,iterations):
                search=Search(query,fields=["message","host"],size=length,start=k*length)
                results=es_conn.search(search)
                for r in results:
                    x =str(remove_unicode(str(r))).split()
                    c_time=(x[1][2:]+' '+x[2])[1:-1]
                    ke=x[4]
                    if ke=="READ":
                        try:
                            ip = x[12][2:-3]
                            ctime = time_to_sec(c_time)
                            index = ctime-min_time + 1
                            size_r = int(x[5].split("=")[1])
                            read_op = int(x[6].split("=")[1])
                            read_active.append([ip,index,size_r,read_op]) 
                        except Exception as e:
                            print e
                    elif ke=="WRITE":
                        try:
                            ip = x[12][2:-3]
                            ctime = time_to_sec(c_time)
                            index = ctime-min_time + 1
                            size_w = int(x[5].split("=")[1])
                            write_op = int(x[6].split("=")[1])
                            write_active.append([ip,index,size_w,write_op])
                        except Exception as e:
                            print e

    if ip_count>0:
        query = BoolQuery(must=[q1,q0,q5])
        search = Search(query,fields=["host"])
        results = es_conn.search(search)
        iterations = len(results)/length + 1

        for k in range(0,iterations):
            search = Search(query,fields=["message","host"],size=length,start=k*length)
            results = es_conn.search(search)
            for r in results:
                x = str(remove_unicode(str(r))).split()
                c_time = (x[1][2:]+' '+x[2])[1:-1]
                ke = x[4]
                if ke == "READ":
                    try:
                        ip = x[12][2:-3]
                        ctime = time_to_sec(c_time)
                        index = ctime-min_time + 1
                        size_r = int(x[5].split("=")[1])
                        read_op = int(x[6].split("=")[1])
                        read_active.append([ip,index,size_r,read_op])
                    except Exception as e:
                        print e
                elif ke=="WRITE":
                    try:
                        ip = x[12][2:-3]
                        ctime = time_to_sec(c_time)
                        index = ctime-min_time + 1
                        size_w = int(x[5].split("=")[1])
                        write_op = int(x[6].split("=")[1])
                        write_active.append([ip,index,size_w,write_op])
                    except Exception as e:
                        print e

def draw_active(data,operation,jobid,min_time,max_time):
    host = dict()
    con = dict()
    count = 0
    for i in range(len(data)):
        if not  (host.has_key((data[i][0],data[i][1]))):
            host[(data[i][0],data[i][1])] = data[i][2]/1024.0
        else:
            host[(data[i][0],data[i][1])] = host[(data[i][0],data[i][1])]+data[i][2]/1024.0

    re = [0.0 for i in range(max_time-min_time+5)]
    for key,value in host.items():
        if value > 50:
            re[key[1]] += 1
    if operation=='read':
        color = 'r'
    elif operation=='write':
        color = 'b'

    plt.plot(re,color,label=operation)
    plt.xlim(0,max_time-min_time)
    plt.title('Job ' + jobid)
    plt.ylabel("Active Process")
    plt.xlabel("Time(s)")
    plt.legend()
    plt.savefig('../pic/'+jobid+'_c'+operation+'_activeprocess.png')
    plt.close()
    #plt.show()

    if operation=='read':
        csvfile = file('../csv/'+jobid+'_cread_activeprocess.csv','wb')
        writer = csv.writer(csvfile)
        writer.writerow(['Process_num'])
        for val in re:
            writer.writerow([val])
        csvfile.close()
    elif operation=='write':
        csvfile = file('../csv/'+jobid+'_cwrite_activeprocess.csv','wb')
        writer = csv.writer(csvfile)
        writer.writerow(['Process_num'])
        for val in re:
            writer.writerow([val])
        csvfile.close()

if __name__=='__main__':
    if (len(sys.argv)==2):
        jobid = sys.argv[1]
    if (len(sys.argv)==6):
        jobid = sys.argv[5]
    job = get_job_by_id(jobid)
    UTC = datetime.timedelta(hours=8)
    for item in job:
        pic_title = item[0] + ' ' + item[1] + ' ' + item[2]
        node_list = item[8]
        start_time = item[3]
        end_time = item[4]
        if end_time == 'None':
            print 'This job is still running.'
        if (len(sys.argv)==2):
            t1 = datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
            t2 = datetime.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
        if (len(sys.argv)==6):
            stime_para = sys.argv[1] + ' ' + sys.argv[2]
            etime_para = sys.argv[3] + ' ' + sys.argv[4]
            if start_time>=stime_para:
                t1 = datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
            else:
                t1 = datetime.datetime.strptime(stime_para,'%Y-%m-%d %H:%M:%S')
            if end_time<=etime_para:
                t2 = datetime.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
            else:
                t2 = datetime.datetime.strptime(etime_para,'%Y-%m-%d %H:%M:%S')
        min_time = time_to_sec(str(t1))
        max_time = time_to_sec(str(t2))
        es_stime = str(t1-UTC)[:10] + 'T' + str(t1-UTC)[11:] + '.000Z'
        es_etime = str(t2-UTC)[:10] + 'T' + str(t2-UTC)[11:] + '.000Z'

        iplist = []
        for node in node_list:
            nodes=node.split('-')
            if len(nodes)>1:
                for x in range(int(nodes[0]),int(nodes[1])+1):
                    w2=x//1024
                    w3=(x-w2*1024)//8
                    w4=x-w2*1024-w3*8+1
                    ip="172."+str(w2)+"."+str(w3)+"."+str(w4)
                    iplist.append(ip)
            elif len(nodes)==1:
                w2=int(nodes[0])//1024
                w3=(int(nodes[0])-w2*1024)//8
                w4=int(nodes[0])-w2*1024-w3*8+1
                ip="172."+str(w2)+"."+str(w3)+"."+str(w4)
                iplist.append(ip)
        
        comput(es_stime,es_etime,iplist)
        draw_active(read_active,'read',str(item[0]),min_time,max_time)
        draw_active(write_active,'write',str(item[0]),min_time,max_time)

