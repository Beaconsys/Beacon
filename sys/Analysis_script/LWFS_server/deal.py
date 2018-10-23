from forwarding_each_all import search_le
from forwarding_each_all import search_gt
from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
import datetime
import time


def get_timelines(time_s, time_e):
    dt_s = datetime.datetime.strptime(time_s, "%Y-%m-%d %H:%M:%S")
    dt_e = datetime.datetime.strptime(time_e, "%Y-%m-%d %H:%M:%S")
    lines = (dt_e - dt_s).seconds
    return lines


def create_csv(data, time_s, time_e):
    columns = [i for i in range(0, 128)]
    csvfile = file('./cache.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(columns)

    timelines = get_timelines(time_s, time_e)
    for i in range(timelines):
        temp = [0 for i in range(0, 128)]
        writer.writerow(temp)

    #p: previous c: current

    host_p = int(data[0].split(' ')[0].split('.')[3]) - 17
    time_p = str(data[0].split(' ')[7])[0:10] + ' ' + str(
        data[0].split(' ')[7])[11:-5]
    line_p = (datetime.datetime.strptime(time_p, "%Y-%m-%d %H:%M:%S") -
              datetime.datetime.strptime(time_s, "%Y-%m-%d %H:%M:%S")).seconds
    #print host_p + "   " + time_p + " line: " + str(line_p)

    matrix_cache_hit = [[0 for i in range(128)] for i in range(timelines)]
    matrix_cache_miss = [[0 for i in range(128)] for i in range(timelines)]
    matrix_discard = [[0 for i in range(128)] for i in range(timelines)]
    #print matrix

    for line in range(1, len(data)):
        host_c = int(data[line].split(' ')[0].split('.')[3]) - 17
        time_c = str(data[line].split(' ')[7][0:10] + ' ' +
                     str(data[line].split(' ')[7])[11:-5])
        line_c = (
            datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") -
            datetime.datetime.strptime(time_s, "%Y-%m-%d %H:%M:%S")).seconds

        cache_hit = int(data[line].split(' ')[2])
        cache_miss = int(data[line].split(' ')[4])
        discard = int(data[line].split(' ')[6])

        #print "current time:" + time_c + "current line: " + str(line_c)

        if host_p == host_c:
            time_delta = (datetime.datetime.strptime(
                time_c, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(
                    time_p, "%Y-%m-%d %H:%M:%S")).seconds
            matrix_cache_hit[line_c][host_c] = cache_hit / time_delta
            matrix_cache_miss[line_c][host_c] = cache_miss / time_delta
            matrix_discard[line_c][host_c] = discard / time_delta
            for j in range(1, time_delta):
                matrix_cache_hit[line_c - j][host_c] = cache_hit / time_delta
                matrix_cache_miss[line_c - j][host_c] = cache_miss / time_delta
                matrix_discard[line_c - j][host_c] = discard / time_delta

            host_p = host_c
            time_p = time_c

        else:
            print "line: " + str(line_c) + " host_c: " + str(host_c)
            #matrix[line_c][host_c] = cache_hit
            host_p = host_c
            time_p = time_c

    np.savetxt("cache_hit.csv", matrix_cache_hit, fmt="%d", delimiter=',')
    np.savetxt("cache_miss.csv", matrix_cache_miss, fmt="%d", delimiter=',')
    np.savetxt("discard.csv", matrix_discard, fmt="%d", delimiter=',')


def get_cache_data(time_s, time_e, hostlist):
    for mon in range(2, 3):
        if mon < 10:
            m = '0' + str(mon)
        else:
            m = str(mon)
        for index_item in range(10, 11):
            bandr = [([0] * 100000) for i in range(130)]
            bandw = [([0] * 100000) for i in range(130)]
            if index_item < 10:
                index = "2018." + m + ".0" + str(index_item)
                daytime = "2017-" + m + "-0" + str(
                    index_item) + " " + "00:00:00"
                time_std = "2017-" + m + "-0" + str(
                    index_item) + " " + "20:00:00"
            else:
                index = "2018." + m + "." + str(index_item)
                daytime = "2017-" + m + "-" + str(
                    index_item) + " " + "00:00:00"
                time_std = "2017-" + m + "-" + str(
                    index_item) + " " + "20:00:00"
            host_t = 87
            print index
            print daytime

        try:
            final_result = search(time_s, time_e, hostlist, index, host_t)
            #print final_result
        except Exception as e:
            print "Error happens during ES Querying"
            print e
            continue

        print "quert done"

        result = []
        for i in xrange(len(final_result[0])):
            host_ip = final_result[0][i]
            message = final_result[1][i]
            time = final_result[2][i]
            result.append(host_ip + ' ' + message + ' ' + time)
            result.sort()

        print "Reshape and sort done..."
        #print result
        for r in result:
            print r

    return result


if __name__ == '__main__':

    hostlist = []
    height = 3000

    time_s = '2018-02-10 10:00:00'
    time_e = '2018-02-10 10:01:00'

    lines = get_timelines(time_s, time_e)

    cache_data = get_cache_data(time_s, time_e, hostlist)

    create_csv(cache_data, time_s, time_e)

#hostlist=[]
#height=3000
#
#messages = []
#columns = [i for i in range(0,128)]
#csvfile = file('./cache.csv', 'wb')
#writer = csv.writer(csvfile)
#writer.writerow(columns)
#writer.writerow([1,2,3])
#line_index = 1
