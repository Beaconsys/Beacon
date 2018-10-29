import sys, json, csv, datetime
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np

from pyes import *
from pyes.aggs import TermsAgg
from pyes.queryset import  QuerySet

from db_util import *
from util import *

length=5000
es_conn=ES('20.0.8.10::9200')
                
def comput(es_stime,es_etime,iplist):
    global min_time,resultr,resultw
    ip_count = 0

    q0 = RangeQuery(qrange = ESRange('@timestamp', from_value = es_stime, to_value = es_etime))
    q1 = ''
    q2 = ''

    q3 = MatchQuery("message", "READ")
    q4 = MatchQuery("message", "WRITE")
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
                    print r
                    x =str(remove_unicode(str(r))).split()
                    c_time=(x[1][2:]+' '+x[2])[1:-1]
                    ke=x[4]
                    if ke=="READ":
                        try:
                            read_size = int(x[5].split("=")[1])
                            ctime = time_to_sec(c_time)
                            index = ctime-min_time + 1
                            resultr[index] += read_size/1024.0
                        except Exception as e:
                            print e
                    elif ke=="WRITE":
                        try:
                            write_size = int(x[5].split("=")[1])
                            ctime = time_to_sec(c_time)
                            index = ctime-min_time + 1
                            resultw[index] += write_size/1024.0
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
                        read_size = int(x[5].split("=")[1])
                        ctime = time_to_sec(c_time)
                        index = ctime-min_time + 1
                        resultr[index] += read_size/1024.0
                    except Exception as e:
                        print e
                elif ke=="WRITE":
                    try:
                        write_size = int(x[5].split("=")[1])
                        ctime = time_to_sec(c_time)
                        index = ctime-min_time + 1
                        resultw[index] += write_size/1024.0
                    except Exception as e:
                        print e

if __name__=='__main__':
    if (len(sys.argv)==2):
        jobid = sys.argv[1]
    if (len(sys.argv)==6):
        jobid = sys.argv[5]
    job = get_job_by_id(jobid)
    UTC = datetime.timedelta(hours=8)
    
    node_list = get_job_node_list(jobid)
    ip_list = get_job_node_ip_list(jobid)
    
    print node_list

    for item in job:
        pic_title = 'Job ' + item[0]
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
        resultr=np.array([0.0 for i in range(max_time-min_time+5)])
        resultw=np.array([0.0 for i in range(max_time-min_time+5)])
        es_stime = str(t1-UTC)[:10] + 'T' + str(t1-UTC)[11:] + '.000Z'
        es_etime = str(t2-UTC)[:10] + 'T' + str(t2-UTC)[11:] + '.000Z'
        
        comput(es_stime,es_etime,iplist)
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

        csvfile=file('../csv/'+str(item[0])+'_ciobandwidth.csv','wb')
        writer=csv.writer(csvfile)
        writer.writerow(['Read','Write'])
        writer.writerows(data)
        csvfile.close()

        plt.plot(resultr,'r',label="Read")
        plt.plot(resultw,'b',label="Write")
        plt.xlabel("Time(s)")
        plt.ylabel("I/O Bandwidth (MB/S)")
        plt.title(str(pic_title))
        plt.legend()
        plt.savefig('../pic/'+str(item[0])+'_ciobandwidth.png')
        #plt.show()
