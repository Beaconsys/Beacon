from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.pyplot import savefig
import numpy as np
import csv
import os
hostlist=[]
bandr=[([0]*100000) for i in range(130)]
bandw=[([0]*100000) for i in range(130)]
sum_r=[0 for i in xrange(100000)]
sum_w=[0 for i in xrange(100000)]
height=300

for index_item  in range(7,8):
    print "start read CSV..."
    count=0
    oscid=[]
    index="2017.05.0"+str(index_item)
    csv_reader=csv.reader(open("./forwarding_CSV/forwardingCSV"+index+'.csv'))
    s=0
    for row in csv_reader:
        for  i in range(0,len(row),2):
            bandr[i/2][s]=float(row[i])
            bandw[i/2][s]=float(row[i+1])
            sum_r[s]+=float(row[i])
            sum_w[s]+=float(row[i+1])
        s+=1
    print "start plot...",s
    flag=1
    if flag==1:
        picnum=0
        ax=plt.gca()
        for i in range(128):
            ax.plot([h+height*count for h in bandr[i]],'r',label='Read')
            ax.plot([h+height*count for h in bandw[i]],'b',label='Write')
            oscid.append('gio'+str(i+17))
            print sum(bandr[i]),'---gio'+str(i+17)
            print sum(bandw[i]),'---gio'+str(i+17)
            count+=1
            if count>=20:
                su=0
                ax.set_yticks(np.linspace(0,count*height,count+1))
                ax.set_yticklabels(oscid)
                plt.ylabel('Forwarding ID')
                plt.xlabel('Time(s)')
                savefig("./forwarding_fig/forwarding_fig"+index+str(picnum)+".png")
                plt.close()
                #plt.show()
                count=0
                oscid=[]
                ax=plt.gca()
                picnum+=1
        if count>0:
            ax.set_yticks(np.linspace(0,count*height,count+1))
            ax.set_yticklabels(oscid)
            plt.ylabel('Forwarding ID')
            plt.xlabel('Time(s)')
            #plt.show()
            savefig("./forwarding_fig/forwarding_fig"+index+str(picnum)+".png")
            plt.close()
    else:
        plt.plot(sum_r,'r',label='Read')
        plt.plot(sum_w,'b',label='Read')
        print sum(sum_r)
        print sum(sum_w)
        plt.ylabel('Aggregate Bandwidth(MB/s)')
        plt.xlabel('Time(s)')
        plt.title(index)
        savefig("./forwarding_fig/forwarding_fig"+index+".png")
        plt.close()





