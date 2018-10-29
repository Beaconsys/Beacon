from forwarding_each_all import search_le
from forwarding_each_all import search_gt
from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
time_s='2018-02-25 10:00:00'
time_e='2018-02-25 10:01:00'
hostlist=[]
height=3000
for mon in range(2,3):
    if mon<10:
        m='0'+str(mon)
    else:
        m=str(mon)
    for index_item in range(25,26):
        bandr=[([0]*100000) for i in range(130)]
        bandw=[([0]*100000) for i in range(130)]
        if index_item<10:
            index="2018."+m+".0"+str(index_item)
            daytime="2017-"+m+"-0"+str(index_item)+" "+"00:00:00"
            time_std="2017-"+m+"-0"+str(index_item)+" "+"20:00:00"
        else:
            index="2018."+m+"."+str(index_item)
            daytime="2017-"+m+"-"+str(index_item)+" "+"00:00:00"
            time_std="2017-"+m+"-"+str(index_item)+" "+"20:00:00"
        host_t=91
        print index
        print daytime

#auto serach,divide one day into two part
        #try:
        #    final_result=search_le(time_std, hostlist, index, host_t)
        #except Exception as e:
        #    print e
        #    continue
        #t1=datetime.datetime.strptime(daytime,'%Y-%m-%d %H:%M:%S')
        #result=[]
        #print "Query1 done..."
        #for i in xrange(len(final_result[0])):
        #    host_ip=final_result[0][i]
        #    message=final_result[1][i]
        #    time=final_result[2][i]
        #    result.append(host_ip+' '+message+' '+time)
        #try:
        #    final_result=search_gt(time_std, hostlist, index, host_t)
        #except Exception as e:
        #    print e
        #    continue
        #print "Query2 done..."
#########################################
#debug
        try:
            final_result=search(time_s, time_e, hostlist, index, host_t)
        except Exception as e:
            print e
            continue
        print "quert done"
#############################################
        result=[]
        for i in xrange(len(final_result[0])):
            host_ip=final_result[0][i]
            message=final_result[1][i]
            time=final_result[2][i]
            result.append(host_ip+' '+message+' '+time)
        result.sort()
        print "Reshape and sort done..."
        for r in result:
            print r
        exit()
#        x=result[0].split(' ')
#        host_p=x[0]
#        ost_p=x[1]
#        read_p=x[2]
#        write_p=x[3]
#        time_p=str(x[4])[:10]+" "+str(x[4])[11:-5]
#        t2=datetime.datetime.strptime(time_p,'%Y-%m-%d %H:%M:%S')
#        time_interval=str(t2-t1).split(':')
#        t_p=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
#        print "Deal data..."
#        for item in range(1,len(final_result[0])):
#            try:
#                y=result[item].split(' ')
#                host=y[0]
#                if host.split('.')[2]=='208':
#                    break
#                ost=y[1]
#                read=y[2]
#                write=y[3]
#                time=str(y[4])[:10]+" "+str(y[4])[11:-5]
#                t3=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
#                time_interval=str(t3-t1).split(':')
#                t=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
#                if host==host_p and ost==ost_p:
#                    host_number=host.split('.')[3]
#                    host_01=host.split('.')[2]
#                    band_number=int(host_number)-17
#                    interval=t-t_p
#                    #print interval," ",t_p," ",band_number
#                    read_value=int(read)-int(read_p)
#                    write_value=int(write)-int(write_p)
#                    if interval>0 and interval<1000:
#                        for j in range(interval):
#                            bandr[band_number][t_p+j]+=read_value/1024.0*4/interval
#                            bandw[band_number][t_p+j]+=write_value/1024.0*4/interval
#                    host_p=host
#                    ost_p=ost
#                    read_p=read
#                    write_p=write
#                    t_p=t
#                else:
#                    x=result[item].split(' ')
#                    host_p=x[0]
#                    ost_p=x[1]
#                    read_p=x[2]
#                    write_p=x[3]
#                    time_p=str(x[4])[:10]+" "+str(x[4])[11:-5]
#                    t2=datetime.datetime.strptime(time_p,'%Y-%m-%d %H:%M:%S')
#                    time_interval=str(t2-t1).split(':')
#                    t_p=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
#            except Exception as e:
#                print e
#                continue
#        print "start write CSV..."
#        ax=plt.gca()
#        count=0
#        oscid=[]
#        csvfile=file("./forwarding_CSV_vbfs/forwardingCSV"+index+'.csv','wb')
#        writer=csv.writer(csvfile)
#        for i in range(100000):
#            row_value=[]
#            for j in range(128):
#                row_value.append(bandr[j][i])
#                row_value.append(bandw[j][i])
#            writer.writerow(row_value)
#        csvfile.close()
        #print "start plot..."
        #for i in range(128):
        #    if np.array(bandr[i]).sum()>0 or np.array(bandw[i]).sum()>0:
        #        ax.plot(np.array(bandr[i])+height*count,'r',label='Read')
        #        ax.plot(np.array(bandw[i])+height*count,'b',label='Write')
        #        oscid.append('gio'+str(i+17))
        #        count+=1
        #        if count>=20:
        #            ax.set_yticks(np.linspace(0,count*height,count+1))
        #            ax.set_yticklabels(oscid)
        #            plt.ylabel('Forwarding ID')
        #            plt.xlabel('Time(s)')
        #            plt.show()
        #            ax=plt.gca()
        #            count=0
        #            oscid=[]

        #if count>0:
        #    ax.set_yticks(np.linspace(0,count*height,count+1))
        #    ax.set_yticklabels(oscid)
        #    plt.ylabel('Forwarding ID')
        #    plt.xlabel('Time(s)')
        #    plt.show()



