import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.pyplot import savefig
import numpy as np
import csv
import os

#MDS_open=[0 for i in xrange(100000)]
#MDS_close=[0 for i in xrange(100000)]
path = './MDS_CSV_vbfs'
re = os.listdir(path)
re.sort()
max_mds = 0
for index in re:
    mon = str(index).split('.')[1]
    day = str(index).split('.')[3]
    c = open(path + '/' + index, 'rb')
    csv_reader = csv.reader(c)
    s = 0
    count_l = 0
    count_m = 0
    count_h = 0
    count_i = 0
    for row in csv_reader:
        MDS_open = float(row[0])
        MDS_close = float(row[1])
        if MDS_open > max_mds:
            max_mds = MDS_open
            max_index = index
            maxtime = s

        if MDS_open < 1000:
            count_i += 1
        elif MDS_open < 2500:
            count_l += 1
        elif MDS_open < 4000:
            count_m += 1
        else:
            count_h += 1
        s += 1
        if s >= 86400:
            break
    c.close()
    print str(
        index
    ), "\t", count_i * 1.0 / 86400, "\t", count_l * 1.0 / 86400, "\t", count_m * 1.0 / 86400, "\t", count_h * 1.0 / 86400
print "max: ", max_mds, " ", max_index, " ", maxtime
#    print "start plot...",s
#    plt.plot(MDS_open,'r',label='Open')
#    plt.plot(MDS_close,'b',label='Close')
#    plt.ylabel('MDS opearation rate')
#    plt.xlabel('Time(s)')
#    plt.title(index)
#    plt.legend()
#    plt.show()
#savefig("./MDS_fig/MDS_fig"+index+".png")
#plt.close()
