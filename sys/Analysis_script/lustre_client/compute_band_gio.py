import datetime
import numpy as np
import csv
import os
file_list = os.listdir("./forwarding_CSV_gio")
file_list.sort()
for file_name in file_list:
    #print file_name
    bandr = [([0] * 100000) for i in range(130)]
    bandw = [([0] * 100000) for i in range(130)]
    sum_r = [0 for i in xrange(100000)]
    sum_w = [0 for i in xrange(100000)]
    csv_reader = csv.reader(open("./forwarding_CSV_gio/" + file_name))
    s = 0
    for row in csv_reader:
        for i in range(0, len(row), 2):
            bandr[i / 2][s] = float(row[i])
            bandw[i / 2][s] = float(row[i + 1])
            sum_r[s] += float(row[i])
            sum_w[s] += float(row[i + 1])
        s += 1
    time = str(file_name.split('.csv')[0]).split('CSV')[1]
    print time, "\t", sum(sum_r), "\t", sum(sum_w)
    #print "strat write csv..."
    index = time
    csvfile = file("./forwarding_band_gio/gio_band" + index + ".csv", 'wb')
    writer = csv.writer(csvfile)
    for i in range(86400):
        row_value = []
        row_value.append(sum_r[i])
        row_value.append(sum_w[i])
        writer.writerow(row_value)
    csvfile.close()
