from MDS_query import search
from MDS_query import search_le
from MDS_query import search_gt
import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
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
    "-n",
    "--need_help",
    default=False,
    action="store_true",
    help="show detail information",
    dest="need_help")
(options, args) = parser.parse_args()

hostlist = []
height = 3000

MDS_open = [0.0 for i in range(86410)]
MDS_close = [0.0 for i in range(86410)]
MDS_open_gio = [0.0 for i in range(86410)]
MDS_close_gio = [0.0 for i in range(86410)]
MDS_open_bio = [0.0 for i in range(86410)]
MDS_close_bio = [0.0 for i in range(86410)]
MDS_open_vbfs = [0.0 for i in range(86410)]
MDS_close_vbfs = [0.0 for i in range(86410)]
MDS_open_psn = [0.0 for i in range(86410)]
MDS_close_psn = [0.0 for i in range(86410)]


def query(time_std, time_s, time_e, hostlist, index, host_t):
    if options.auto == True:
        try:
            final_result = search_le(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
        result = []
        print "Query1 done..."
        ll = len(final_result[1])
        for i in xrange(ll):
            host = final_result[0][i].split(' ')[0]
            time = final_result[1][i]
            message = final_result[0][i].split(' ')[1:]
            result.append([host, time, message])
        try:
            final_result = search_gt(time_std, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        ll = len(final_result[1])
        for i in xrange(ll):
            host = final_result[0][i].split(' ')[0]
            time = final_result[1][i]
            message = final_result[0][i].split(' ')[1:]
            result.append([host, time, message])
        print "Query2 done..."
    else:
        try:
            final_result = search(time_s, time_e, hostlist, index, host_t)
        except Exception as e:
            print e
            return 0
        t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
        result = []
        print "Query done..."
        ll = len(final_result[1])
        for i in xrange(ll):
            host = final_result[0][i].split(' ')[0]
            time = final_result[1][i]
            message = final_result[0][i].split(' ')[1:]
            result.append([host, time, message])
        result.sort()
        print "Reshape and sort done..."
    return result, t1


def deal_data(result, index, t1):
    global MDS_open, MDS_close, MDS_open_gio, MDS_close_gio, MDS_open_bio, \
    MDS_close_bio, MDS_open_vbfs, MDS_close_vbfs, MDS_open_psn, MDS_close_psn
    x = result[0][2]
    ll = len(result)
    st = 0
    while 1:
        while len(x) <= 1 and st < ll:
            st += 1
            x = result[st][2]

        if st < ll:
            try:
                host_p = result[st][0]
                operation = x[0]
                if operation <> 'open':
                    continue
                samples_open_p = x[1]
                samples_close_p = x[3]
                time_p = str(result[st][1])[:10] + " " + str(
                    result[st][1])[11:-5]
                t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
                time_interval = str(t2 - t1).split(':')
                t_p = int(time_interval[0]) * 3600 + int(
                    time_interval[1]) * 60 + int(time_interval[2])
                break
            except Exception as e:
                print e
                continue
        else:
            exit
    print host_p, operation, samples_open_p, samples_close_p, time_p
    print "Deal data..."

    for item in range(st + 1, ll):
        try:
            y = result[item][2]
            host = result[item][0]
            operation = y[0]
            if operation <> 'open':
                continue
            samples_open = y[1]
            samples_close = y[3]
            time = str(result[item][1])[:10] + " " + str(
                result[item][1])[11:-5]
            t3 = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time_interval = str(t3 - t1).split(':')
            t = int(time_interval[0]) * 3600 + int(
                time_interval[1]) * 60 + int(time_interval[2])
            if host == host_p:
                #host_number=host.split('.')[3]
                #host_01=host.split('.')[2]
                #band_number=int(host_number)-17
                interval = t - t_p
                #print interval," ",t_p," ",band_number
                value_open = int(samples_open) - int(samples_open_p)
                value_close = int(samples_close) - int(samples_close_p)
                if interval > 0:
                    #print result[item][0]," ",result[item][1]," ",result[item][2]
                    for j in range(interval):
                        MDS_open[t_p + j] += value_open * 1.0 / interval
                        MDS_close[t_p + j] += value_close * 1.0 / interval
                    if '17.0.2.' in result[item][0]:
                        for j in range(interval):
                            MDS_open_gio[t_p +
                                         j] += value_open * 1.0 / interval
                            MDS_close_gio[t_p +
                                          j] += value_close * 1.0 / interval
                    elif '17.0.208.' in result[item][0]:
                        for j in range(interval):
                            MDS_open_vbfs[t_p +
                                          j] += value_open * 1.0 / interval
                            MDS_close_vbfs[t_p +
                                           j] += value_close * 1.0 / interval
                    elif '17.0.15.' in result[item][0]:
                        for j in range(interval):
                            MDS_open_psn[t_p +
                                         j] += value_open * 1.0 / interval
                            MDS_close_psn[t_p +
                                          j] += value_close * 1.0 / interval
                    elif '17.0.8.' in result[item][0]:
                        for j in range(interval):
                            MDS_open_bio[t_p +
                                         j] += value_open * 1.0 / interval
                            MDS_close_bio[t_p +
                                          j] += value_close * 1.0 / interval
                host_p = host
                samples_open_p = samples_open
                samples_close_p = samples_close
                t_p = t
            else:
                x = result[item][2]
                host_p = result[item][0]
                operation = x[0]
                if operation <> 'open':
                    continue
                samples_open_p = x[1]
                samples_close_p = x[3]
                time_p = str(result[item][1])[:10] + " " + str(
                    result[item][1])[11:-5]
                t2 = datetime.datetime.strptime(time_p, '%Y-%m-%d %H:%M:%S')
                time_interval = str(t2 - t1).split(':')
                t_p = int(time_interval[0]) * 3600 + int(
                    time_interval[1]) * 60 + int(time_interval[2])
        except Exception as e:
            print e
            continue

    if options.trace == True:
        print "start write CSV..."
        count = 0
        csvfile = file("../Trace/lustre_MDS/total/" + index + '.csv', 'wb')
        writer = csv.writer(csvfile)
        for i in range(86410):
            row_value = []
            row_value.append(i)
            row_value.append(MDS_open[i])
            row_value.append(MDS_close[i])
            if MDS_open[i] > 0 or MDS_close[i] > 0:
                writer.writerow(row_value)
        csvfile.close()

        print "start write CSV---gio..."
        count = 0
        csvfile = file("../Trace/lustre_MDS/gio/" + index + '.csv', 'wb')
        writer = csv.writer(csvfile)
        for i in range(86410):
            row_value = []
            row_value.append(i)
            row_value.append(MDS_open_gio[i])
            row_value.append(MDS_close_gio[i])
            if MDS_open_gio[i] > 0 or MDS_close_gio[i] > 0:
                writer.writerow(row_value)
        csvfile.close()

        print "start write CSV---bio..."
        count = 0
        csvfile = file("../Trace/lustre_MDS/bio/" + index + '.csv', 'wb')
        writer = csv.writer(csvfile)
        for i in range(86410):
            row_value = []
            row_value.append(i)
            row_value.append(MDS_open_bio[i])
            row_value.append(MDS_close_bio[i])
            if MDS_open_bio[i] > 0 or MDS_close_bio[i] > 0:
                writer.writerow(row_value)
        csvfile.close()

        print "start write CSV---psn..."
        count = 0
        csvfile = file("../Trace/lustre_MDS/psn/" + index + '.csv', 'wb')
        writer = csv.writer(csvfile)
        for i in range(86410):
            row_value = []
            row_value.append(i)
            row_value.append(MDS_open_psn[i])
            row_value.append(MDS_close_psn[i])
            if MDS_open_psn[i] > 0 or MDS_close_psn[i] > 0:
                writer.writerow(row_value)
        csvfile.close()

        print "start write CSV---vbfs..."
        count = 0
        csvfile = file("../Trace/lustre_MDS/vbfs/" + index + '.csv', 'wb')
        writer = csv.writer(csvfile)
        for i in range(86410):
            row_value = []
            row_value.append(i)
            row_value.append(MDS_open_vbfs[i])
            row_value.append(MDS_close_vbfs[i])
            if MDS_open_vbfs[i] > 0 or MDS_close_vbfs[i] > 0:
                writer.writerow(row_value)
        csvfile.close()

    if options.draw == True:
        print "start plot..."
        plt.plot(MDS_open, 'r', label='Open')
        plt.plot(MDS_close, 'b', label='Close')
        plt.ylabel('MDS opearation rate')
        plt.xlabel('Time(s)')
        plt.legend()
        plt.show()
        #savefig("./MDS_fig/MDS_fig"+index+".png")
        #plt.close()

        print "start plot--gio..."
        plt.plot(MDS_open_gio, 'r', label='Open')
        plt.plot(MDS_close_gio, 'b', label='Close')
        plt.ylabel('MDS opearation rate')
        plt.xlabel('Time(s)')
        plt.legend()
        plt.show()
        #savefig("./MDS_fig_gio/MDS_fig"+index+".png")
        #plt.close()

        print "start plot--bio..."
        plt.plot(MDS_open_bio, 'r', label='Open')
        plt.plot(MDS_close_bio, 'b', label='Close')
        plt.ylabel('MDS opearation rate')
        plt.xlabel('Time(s)')
        plt.legend()
        plt.show()
        #savefig("./MDS_fig_bio/MDS_fig"+index+".png")
        #plt.close()

        print "start plot--vbfs..."
        plt.plot(MDS_open_vbfs, 'r', label='Open')
        plt.plot(MDS_close_vbfs, 'b', label='Close')
        plt.ylabel('MDS opearation rate')
        plt.xlabel('Time(s)')
        plt.legend()
        #plt.show()
        #savefig("./MDS_fig_vbfs/MDS_fig"+index+".png")
        #plt.close()

        print "start plot--psn..."
        plt.plot(MDS_open_psn, 'r', label='Open')
        plt.plot(MDS_close_psn, 'b', label='Close')
        plt.ylabel('MDS opearation rate')
        plt.xlabel('Time(s)')
        plt.legend()
        plt.show()
        #savefig("./MDS_fig_psn/MDS_fig"+index+".png")
        #plt.close()


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
    if len(sys.argv) < 5:
        print "please input start_time,end_time (2018-03-02 10:00:00 2018-03-27 14:01:39)"
        sys.exit()
    else:
        print len(sys.argv)
        time_s = sys.argv[1] + " " + sys.argv[2]
        time_e = sys.argv[3] + " " + sys.argv[4]
        month_s = int(sys.argv[1].split('-')[1])
        month_e = int(sys.argv[3].split('-')[1])
        day_s = int(sys.argv[1].split('-')[2])
        day_e = int(sys.argv[3].split('-')[2])
        host_t = 86
    for mon in range(month_s, month_e + 1):
        if mon < 10:
            m = "0" + str(mon)
        else:
            m = str(mon)
        for index_item in range(day_s, day_e + 1):
            hostlist = []
            MDS_open = [0.0 for i in range(86410)]
            MDS_close = [0.0 for i in range(86410)]
            MDS_open_gio = [0.0 for i in range(86410)]
            MDS_close_gio = [0.0 for i in range(86410)]
            MDS_open_bio = [0.0 for i in range(86410)]
            MDS_close_bio = [0.0 for i in range(86410)]
            MDS_open_vbfs = [0.0 for i in range(86410)]
            MDS_close_vbfs = [0.0 for i in range(86410)]
            MDS_open_psn = [0.0 for i in range(86410)]
            MDS_close_psn = [0.0 for i in range(86410)]
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
            result, t1 = query(time_std, time_s, time_e, hostlist, index,
                               host_t)
            deal_data(result, index, t1)
