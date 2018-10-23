from forwarding_each_all import search_le
from forwarding_each_all import search_gt
from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option(
    "-d",
    "--draw",
    default=False,
    action="store_true",
    help="Draw the figures",
    dest="draw")
parser.add_option(
    "-t",
    "--trace",
    default=False,
    action="store_true",
    help="save trace",
    dest="trace")
parser.add_option(
    "-a",
    "--auto",
    default=False,
    action="store_true",
    help="run with automatic mode",
    dest="auto")
parser.add_option(
    "-o",
    "--old",
    default=False,
    action="store_true",
    help="deal old format data",
    dest="old")
parser.add_option(
    "-c",
    "--cache",
    default=False,
    action="store_true",
    help="deal cache result",
    dest="cache")
parser.add_option(
    "-b",
    "--band",
    default=False,
    action="store_true",
    help="deal band result",
    dest="band")
parser.add_option(
    "-n",
    "--need_help",
    default=False,
    action="store_true",
    help="show detail information",
    dest="need_help")
(options, args) = parser.parse_args()

height = 3000
hit_list = [([0] * 86410) for i in range(130)]
miss_list = [([0] * 86410) for i in range(130)]
discard_list = [([0] * 86410) for i in range(130)]
bandr = [([0] * 86410) for i in range(130)]
bandw = [([0] * 86410) for i in range(130)]
host_t = 87
result_cache = []
result_band = []
t1 = datetime.datetime.strptime('2018-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
index = '2018.01.01'


def query(index, daytime, time_std, time_s, time_e, hostlist):
    global host_t, hit_list, miss_list, discard_list, bandr, bandw, result_cache, result_band, t1
    if options.auto == True:
        try:
            final_result = search_le(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        print "Query1 done..."
        for i in xrange(len(final_result[0])):
            host_ip = final_result[0][i]
            message = final_result[1][i]
            time = final_result[2][i]
            if "cache" in message:
                result_cache.append(host_ip + ' ' + message + ' ' + time)
            else:
                result_band.append(host_ip + ' ' + message + ' ' + time)
        try:
            final_result = search_gt(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        print "Query2 done..."
        for i in xrange(len(final_result[0])):
            host_ip = final_result[0][i]
            message = final_result[1][i]
            time = final_result[2][i]
            if "cache" in message:
                result_cache.append(host_ip + ' ' + message + ' ' + time)
            else:
                result_band.append(host_ip + ' ' + message + ' ' + time)
    else:
        try:
            final_result = search(time_s, time_e, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        print "quert done"
        for i in xrange(len(final_result[0])):
            host_ip = final_result[0][i]
            message = final_result[1][i]
            time = final_result[2][i]
            if "cache" in message:
                result_cache.append(host_ip + ' ' + message + ' ' + time)
            else:
                result_band.append(host_ip + ' ' + message + ' ' + time)


def deal_cache():
    global result_cache, host_t, hit_list, miss_list, discard, t1
    result_cache.sort()
    print "Reshape and sort done..."
    lg = len(result_cache)
    print lg
    print result_cache[0]
    x = result_cache[0].split(' ')
    host_p = x[0]
    cache_hit_p = int(x[2])
    cache_miss_p = int(x[4])
    discard_p = int(x[6])
    time_p = str(x[7])[:10] + " " + str(x[7][11:-5])
    t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
    time_interval = str(t2 - t1).split(":")
    t_p = int(time_interval[0]) * 3600 + int(time_interval[1]) * 60 + int(
        time_interval[2])
    print "Deal data..."
    for item in range(1, lg):
        try:
            y = result_cache[item].split(' ')
            host = y[0]
            #                    if host.split('.')[2] == '208':
            #                        break
            cache_hit = int(y[2])
            cache_miss = int(y[4])
            discard = int(y[6])
            time = str(y[7])[:10] + " " + str(y[7])[11:-5]
            t3 = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time_interval = str(t3 - t1).split(':')
            t = int(time_interval[0]) * 3600 + int(
                time_interval[1]) * 60 + int(time_interval[2])
            if host == host_p:
                host_number = host.split('.')[3]
                if host_t == 87:
                    band_number = int(host_number) - 17
                else:
                    band_number = int(host_number)
                interval = t - t_p
                #print interval," ",t_p," ",band_number
                hit_value = int(cache_hit) - int(cache_hit_p)
                miss_value = int(cache_miss) - int(cache_miss_p)
                discard_value = int(discard) - int(discard_p)
                if interval > 0 and interval < 1000:
                    for j in range(interval):
                        hit_list[band_number][
                            t_p + j] += hit_value / 1024.0 * 4 / interval
                        miss_list[band_number][
                            t_p + j] += miss_value / 1024.0 * 4 / interval
                        discard_list[band_number][
                            t_p + j] += discard_value / 1024.0 * 4 / interval
                host_p = host
                cache_hit_p = cache_hit
                cache_miss_p = cache_miss
                discard_p = discard
                t_p = t
            else:
                x = result_cache[item].split(' ')
                host_p = x[0]
                cache_hit_p = int(x[2])
                cache_miss_p = int(x[4])
                discard_p = int(x[6])
                time_p = str(x[7])[:10] + " " + str(x[7][11:-5])
                t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
                time_interval = str(t2 - t1).split(":")
                t_p = int(time_interval[0]) * 3600 + int(
                    time_interval[1]) * 60 + int(time_interval[2])
        except Exception as e:
            print e
            continue


def deal_band():
    global result_band, host_t, bandr, bandw, t1
    if options.old == True:
        result_band.sort()
        print "Reshape and sort done..."
        print len(result_band)
        print result_band[0]
        x = result_band[0].split(' ')
        host_p = x[0]
        ost_p = x[1]
        read_p = x[2]
        write_p = x[3]
        time_p = str(x[4])[:10] + " " + str(x[4])[11:-5]
        t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
        time_interval = str(t2 - t1).split(':')
        t_p = int(time_interval[0]) * 3600 + int(time_interval[1]) * 60 + int(
            time_interval[2])
        print "Deal data..."
        for item in range(1, len(final_result[0])):
            try:
                y = result_band[item].split(' ')
                host = y[0]
                #                if host.split('.')[2]=='208':
                #                    break
                ost = y[1]
                read = y[2]
                write = y[3]
                time = str(y[4])[:10] + " " + str(y[4])[11:-5]
                t3 = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                time_interval = str(t3 - t1).split(':')
                t = int(time_interval[0]) * 3600 + int(
                    time_interval[1]) * 60 + int(time_interval[2])
                if host == host_p and ost == ost_p:
                    host_number = host.split('.')[3]
                    #host_01=host.split('.')[2]
                    if host_t == 87:
                        band_number = int(host_number) - 17
                    else:
                        band_number = int(host_number)
                    interval = t - t_p
                    #print interval," ",t_p," ",band_number
                    read_value = int(read) - int(read_p)
                    write_value = int(write) - int(write_p)
                    if interval > 0 and interval < 1000:
                        for j in range(interval):
                            bandr[band_number][
                                t_p + j] += read_value / 1024.0 * 4 / interval
                            bandw[band_number][
                                t_p + j] += write_value / 1024.0 * 4 / interval
                    host_p = host
                    ost_p = ost
                    read_p = read
                    write_p = write
                    t_p = t
                else:
                    x = result_band[item].split(' ')
                    host_p = x[0]
                    ost_p = x[1]
                    read_p = x[2]
                    write_p = x[3]
                    time_p = str(x[4])[:10] + " " + str(x[4])[11:-5]
                    t2 = datetime.datetime.strptime(time_p,
                                                    '%Y-%m-%d %H:%M:%S')
                    time_interval = str(t2 - t1).split(':')
                    t_p = int(time_interval[0]) * 3600 + int(
                        time_interval[1]) * 60 + int(time_interval[2])
            except Exception as e:
                print e
                continue
    else:
        result_band.sort()
        print "Reshape and sort done..."
        print len(result_band)
        #                for r in result_band:
        #                    print r
        s1 = result_band[0].replace(',', '')
        s2 = s1.replace('[', '')
        s3 = s2.replace(']', '')
        x = s3.split(' ')
        host_p = x[0]
        ost_p = x[1]
        print x
        print x[-1]
        time_p = str(x[-1])[:10] + " " + str(x[-1])[11:-5]
        t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
        time_interval = str(t2 - t1).split(':')
        t_p = int(time_interval[0]) * 3600 + int(time_interval[1]) * 60 + int(
            time_interval[2])
        read_p = 0
        write_p = 0
        for i in range(2, len(x) - 1, 3):
            read_p += int(x[i]) * int(x[i + 1])
            write_p += int(x[i]) * int(x[i + 2])
        print ost_p, " ", read_p, " ", write_p, " ", time_p
        print "Deal data..."
        for item in range(1, len(result_band)):
            try:
                s1 = result_band[item].replace(',', '')
                s2 = s1.replace('[', '')
                s3 = s2.replace(']', '')
                y = s3.split(' ')
                host = y[0]
                ost = y[1]
                time = str(y[-1])[:10] + " " + str(y[-1])[11:-5]
                t3 = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                time_interval = str(t3 - t1).split(':')
                t = int(time_interval[0]) * 3600 + int(
                    time_interval[1]) * 60 + int(time_interval[2])
                read = 0
                write = 0
                for i in range(2, len(y) - 1, 3):
                    read += int(y[i]) * int(y[i + 1])
                    write += int(y[i]) * int(y[i + 2])
                if host == host_p and ost == ost_p:
                    host_number = host.split('.')[3]
                    #host_01=host.split('.')[2]
                    if host_t == 87:
                        band_number = int(host_number) - 17
                    else:
                        band_number = int(host_number)
                    interval = t - t_p
                    #print interval," ",t_p," ",band_number
                    read_value = int(read) - int(read_p)
                    write_value = int(write) - int(write_p)
                    #print read_value," ",write_value," ",interval
                    if interval > 0 and interval < 1000:
                        for j in range(interval):
                            bandr[band_number][
                                t_p + j] += read_value / 1024.0 * 4 / interval
                            bandw[band_number][
                                t_p + j] += write_value / 1024.0 * 4 / interval
                    host_p = host
                    ost_p = ost
                    read_p = read
                    write_p = write
                    t_p = t
                else:
                    host_p = host
                    ost_p = ost
                    read_p = read
                    write_p = write
                    t_p = t
            except Exception as e:
                print e
                continue


def save_trace():
    global banr, banw, hit_list, miss_list, discard_list, host_t, index
    print "start write CSV..."
    if host_t == 87:
        csvfile = file("../Trace/lustre_client/gio/" + index + '.csv', 'wb')
        jj = 17
    else:
        csvfile = file("../Trace/lustre_client/vbfs/" + index + '.csv', 'wb')
        jj = 0
    writer = csv.writer(csvfile)
    for j in range(128):
        for i in range(86410):
            row_value = []
            row_value.append(j + jj)
            row_value.append(i)
            row_value.append(bandr[j][i])
            row_value.append(bandw[j][i])
            row_value.append(hit_list[j][i])
            row_value.append(miss_list[j][i])
            row_value.append(discard_list[j][i])
            if hit_list[j][i] > 0 or miss_list[j][i] > 0 or \
                discard_list[j][i] > 0 or bandr[j][i] > 0 or bandw[j][i] > 0:
                #print row_value
                writer.writerow(row_value)
    csvfile.close()


def draw_pic():
    global banr, banw, hit_list, miss_list, discard_list, host_t, index, height
    #print "plot is not supported..."
    ax = plt.gca()
    count = 0
    oscid = []
    if host_t == 87:
        jj = 17
        fwd = 'gio'
    else:
        jj = 0
        fwd = 'vbfs'

    for i in range(128):
        if np.array(bandr[i]).sum() > 0 or np.array(bandw[i]).sum() > 0:
            ax.plot(np.array(bandr[i]) + height * count, 'r', label='Read')
            ax.plot(np.array(bandw[i]) + height * count, 'b', label='Write')
            oscid.append(fwd + str(i + jj))
            count += 1
            if count >= 20:
                ax.set_yticks(np.linspace(0, count * height, count + 1))
                ax.set_yticklabels(oscid)
                plt.ylabel('Forwarding ID')
                plt.xlabel('Time(s)')
                plt.show()
                ax = plt.gca()
                count = 0
                oscid = []
    if count > 0:
        ax.set_yticks(np.linspace(0, count * height, count + 1))
        ax.set_yticklabels(oscid)
        plt.ylabel('Forwarding ID')
        plt.xlabel('Time(s)')
        plt.show()


if __name__ == "__main__":
    time_s = '2018-03-27 13:59:37'
    time_e = '2018-03-27 14:01:39'
    if options.need_help == True:
        print "you can use this script like this:python lustre_client_band_cache.py 2018-08-01 09:50:00 2018-08-01 09:52:00 vbfs (vbfs can replace with gio)"
        print "Also, you can use some triggers"
        print "-d mean draw pic"
        print "-t save trace"
        print "-o deal old format data"
        print "-b get bandwidht"
        print "-c get cache information"
        print "-a run with automatic (use to get lots of data)"
        print "-n need help information"
        sys.exit()

    if len(sys.argv) < 6:
        print "please input start_time,end_time and gio/vbfs (2018-03-02 10:00:00 2018-03-27 14:01:39 gio)"
        sys.exit()
    else:
        print len(sys.argv)
        time_s = sys.argv[1] + " " + sys.argv[2]
        time_e = sys.argv[3] + " " + sys.argv[4]
        hostlist = []
        month_s = int(sys.argv[1].split('-')[1])
        month_e = int(sys.argv[3].split('-')[1])
        day_s = int(sys.argv[1].split('-')[2])
        day_e = int(sys.argv[3].split('-')[2])
        if sys.argv[5] == 'gio':
            host_t = 87
        else:
            host_t = 89
        for mon in range(month_s, month_e + 1):
            if mon < 10:
                m = '0' + str(mon)
            else:
                m = str(mon)
            for index_item in range(day_s, day_e + 1):
                if index_item < 10:
                    index = "2018." + m + ".0" + str(index_item)
                    daytime = "2018-" + m + "-0" + str(
                        index_item) + " " + "00:00:00"
                    time_std = "2018-" + m + "-0" + str(
                        index_item) + " " + "12:00:00"
                else:
                    index = "2018." + m + "." + str(index_item)
                    daytime = "2018-" + m + "-" + str(
                        index_item) + " " + "00:00:00"
                    time_std = "2018-" + m + "-" + str(
                        index_item) + " " + "12:00:00"
                print index
                print daytime
                t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
            hit_list = [([0] * 86410) for i in range(130)]
            miss_list = [([0] * 86410) for i in range(130)]
            discard_list = [([0] * 86410) for i in range(130)]
            bandr = [([0] * 86410) for i in range(130)]
            bandw = [([0] * 86410) for i in range(130)]
            query(index, daytime, time_std, time_s, time_e, hostlist)
            if options.cache == True:
                deal_cache()
            if options.band == True:
                deal_band()
            if options.trace == True:
                save_trace()
            if options.draw == True:
                draw_pic()
