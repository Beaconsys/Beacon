from OST_each_all import search
from OST_each_all import search_le
from OST_each_all import search_gt
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys
from optparse import OptionParser

host_online1 = null
host_online2 = null

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
#parser.add_option("-o", "--old", default = False, action = "store_true", help = "deal old format data", dest = "old")
parser.add_option(
    "-n",
    "--need_help",
    default=False,
    action="store_true",
    help="show detail information",
    dest="need_help")
(options, args) = parser.parse_args()

height = 300


def query(bandr, bandw, host_t, index, daytime, time_std, time_s, time_e,
          hostlist):
    if options.auto == True:
        try:
            final_result = search_le(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
        result = []
        print "Query1 done..."
        for i in xrange(len(final_result[0])):
            message = final_result[0][i]
            time = final_result[1][i]
            result.append(message + ' ' + time)
        try:
            final_result = search_gt(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        for i in xrange(len(final_result[0])):
            message = final_result[0][i]
            time = final_result[1][i]
            result.append(message + ' ' + time)
        print "Query2 done..."
        result.sort()
        print "Reshape and sort done..."
    else:
        try:
            final_result = search(time_s, time_e, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
        result = []
        print "Test Query done..."
        for i in xrange(len(final_result[0])):
            message = final_result[0][i]
            time = final_result[1][i]
            result.append(message + ' ' + time)
        result.sort()

    lg = len(result)
    print result[0]
    s1 = result[0].replace(',', '')
    s2 = s1.replace('[', '')
    s3 = s2.replace(']', '')
    x = s3.split(' ')
    ost_p = x[0]
    print x
    print x[-1]
    time_p = str(x[-1])[:10] + " " + str(x[-1])[11:-5]
    t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
    time_interval = str(t2 - t1).split(':')
    t_p = int(time_interval[0]) * 3600 + int(time_interval[1]) * 60 + int(
        time_interval[2])
    read_p = 0
    write_p = 0
    for i in range(1, len(x) - 1, 3):
        read_p += int(x[i]) * int(x[i + 1])
        write_p += int(x[i]) * int(x[i + 2])
    print ost_p, " ", read_p, " ", write_p, " ", time_p
    print "Deal data..."
    for item in range(1, lg):
        try:
            s1 = result[item].replace(',', '')
            s2 = s1.replace('[', '')
            s3 = s2.replace(']', '')
            y = s3.split(' ')
            ost = y[0]
            time = str(y[-1])[:10] + " " + str(y[-1])[11:-5]
            t3 = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time_interval = str(t3 - t1).split(':')
            t = int(time_interval[0]) * 3600 + int(
                time_interval[1]) * 60 + int(time_interval[2])
            read = 0
            write = 0
            for i in range(1, len(x) - 1, 3):
                read += int(y[i]) * int(y[i + 1])
                write += int(y[i]) * int(y[i + 2])
            if ost == ost_p:
                interval = t - t_p
                #print interval," ",t_p," ",band_number
                OST_number = int('0x' + ost, 16)
                read_value = int(read) - int(read_p)
                write_value = int(write) - int(write_p)
                if interval > 0 and interval < 1000:
                    for j in range(interval):
                        bandr[OST_number][
                            t_p + j] += read_value / 1024.0 * 4 / interval
                        bandw[OST_number][
                            t_p + j] += write_value / 1024.0 * 4 / interval
                ost_p = ost
                read_p = read
                write_p = write
                t_p = t
            else:
                ost_p = ost
                read_p = read
                write_p = write
                t_p = t
        except Exception as e:
            print e
            continue

    if options.trace == True:
        print "start write CSV..."
        count = 0
        oscid = []
        if host_t == host_online1:
            csvfile = file("../Trace/lustre_client/gio/" + index + '.csv',
                           'wb')
        else:
            csvfile = file("../Trace/lustre_client/vbfs/" + index + '.csv',
                           'wb')
        writer = csv.writer(csvfile)
        for j in range(440):
            for i in range(100000):
                row_value = []
                row_value.append(j)
                row_value.append(i)
                row_value.append(bandr[j][i])
                row_value.append(bandw[j][i])
                if bandr[j][i] > 0 or bandw[j][i] > 0:
                    writer.writerow(row_value)
        csvfile.close()

    if options.draw == True:
        print "start plot..."
        ax = plt.gca()
        for i in range(440):
            if np.array(bandr[i]).sum() > 0 or np.array(bandw[i]).sum() > 0:
                ax.plot(np.array(bandr[i]) + height * count, 'r', label='Read')
                ax.plot(
                    np.array(bandw[i]) + height * count, 'b', label='Write')
                oscid.append(str(hex(i)))
                count += 1
                if count >= 20:
                    ax.set_yticks(np.linspace(0, count * height, count + 1))
                    ax.set_yticklabels(oscid)
                    plt.ylabel('OST ID')
                    plt.xlabel('Time(s)')
                    plt.show()
                    ax = plt.gca()
                    count = 0
                    oscid = []

        if count > 0:
            ax.set_yticks(np.linspace(0, count * height, count + 1))
            ax.set_yticklabels(oscid)
            plt.ylabel('OST ID')
            plt.xlabel('Time(s)')
            plt.show()


if __name__ == "__main__":
    time_s = '2018-02-02 10:00:00'
    time_e = '2018-02-02 10:10:00'
    if options.need_help == True:
        print "you can use this script like this: python lustre_server_band.py 2018-01-01 09:00:00 2018-01-01 09:10:00 vbfs (vbfs can replace with gio)"
        print "Also, you can use some triggers"
        print "-d mean draw pic"
        print "-t save trace"
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
        month_s = int(sys.argv[1].split('-')[1])
        month_e = int(sys.argv[3].split('-')[1])
        day_s = int(sys.argv[1].split('-')[2])
        day_e = int(sys.argv[3].split('-')[2])
        if sys.argv[5] == 'gio':
            host_t = host_online1
        else:
            host_t = host_online2
    for mon in range(month_s, month_e + 1):
        if mon < 10:
            m = "0" + str(mon)
        else:
            m = str(mon)
        for index_item in range(day_s, day_e + 1):
            hostlist = []
            bandr = [([0] * 100000) for i in range(440)]
            bandw = [([0] * 100000) for i in range(440)]
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
            query(bandr, bandw, host_t, index, daytime, time_std, time_s,
                  time_e, hostlist)
