from forwarding_each_all import search_le
from forwarding_each_all import search_gt
from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv


def get_timelines(time_s, time_e):
    dt_s = datetime.datetime.strptime(time_s, "%Y-%m-%d %H:%M:%S")
    dt_e = datetime.datetime.strptime(time_e, "%Y-%m-%d %H:%M:%S")
    lines = (dt_e - dt_s).seconds

    return lines


def deal_queue(queues, time_s, time_e):
    timelines = get_timelines(time_s, time_e)
    time_a = datetime.datetime.strptime(
        time_s, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)

    host_h = int(queues[0].split(' ')[0].split('.')[3]) - 17
    time_h = queues[0].split(' ')[1][1:] + ' ' + queues[0].split(' ')[2][0:-1]
    line_h = (datetime.datetime.strptime(time_h, "%Y-%m-%d %H:%M:%S") -
              time_a).seconds
    val_h = int(queues[0].split(' ')[7])

    matrix = [[0 for i in range(128)] for i in range(timelines)]

    #print "lendth: " + str(len(queues))
    file_line = len(queues)

    for line in range(1, file_line - 1):
        #print "Dealing line: " + str(line)
        time_c = queues[line].split(' ')[1][1:] + ' ' + queues[line].split(
            ' ')[2][0:-1]
        time_next = queues[line + 1].split(' ')[1][1:] + ' ' + queues[
            line + 1].split(' ')[2][0:-1]
        line_c = (datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") -
                  time_a).seconds
        host_c = int(queues[line].split(' ')[0].split('.')[3]) - 17
        val_c = int(queues[line].split(' ')[7])

        if time_next == time_c:
            continue
        else:
            matrix[line_c][host_c] = val_c - val_h
            val_h = int(queues[line + 1].split(' ')[7])

    np.savetxt("./csv_data/queue.csv", matrix, fmt="%d", delimiter=",")


def create_csv(data, time_s, time_e):
    #t: tail c: current  h: head
    #op: operation

    timelines = get_timelines(time_s, time_e)
    time_a = datetime.datetime.strptime(
        time_s, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)

    host_h = int(data[0].split(' ')[0].split('.')[3]) - 17
    time_h = data[0].split(' ')[1][1:] + ' ' + data[0].split(' ')[2][0:-1]
    line_h = (datetime.datetime.strptime(time_h, "%Y-%m-%d %H:%M:%S") -
              time_a).seconds
    op_h = data[0].split(' ')[5] + '_' + data[0].split(' ')[6]

    for i in range(0, 8):
        locals()['varh_' + str(i)] = int(data[0].split(' ')[7 + i])
        print locals()['varh_' + str(i)]
    matrix_rw = [[0 for i in range(128 * 9)] for i in range(timelines)]
    matrix_re = [[0 for i in range(128 * 9)] for i in range(timelines)]
    matrix_ww = [[0 for i in range(128 * 9)] for i in range(timelines)]
    matrix_we = [[0 for i in range(128 * 9)] for i in range(timelines)]
    matrix_mw = [[0 for i in range(128 * 9)] for i in range(timelines)]
    matrix_me = [[0 for i in range(128 * 9)] for i in range(timelines)]

    #print "lendth: " + str(len(data))
    file_line = len(data)
    for line in range(1, file_line - 1):
        #print "Dealing line: " + str(line)
        op_c = data[line].split(' ')[5] + '_' + data[line].split(' ')[6][0:-1]
        op_next = data[line +
                       1].split(' ')[5] + '_' + data[line].split(' ')[6][0:-1]

        if op_next == op_c:
            continue
        else:
            host_c = int(data[line].split(' ')[0].split('.')[3]) - 17
            time_c = data[line].split(' ')[1][1:] + ' ' + data[line].split(
                ' ')[2][0:-1]
            line_c = (datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") -
                      time_a).seconds

            #print "ROW: " + str(line_c) #OK

            for i in range(0, 8):
                #print line
                locals()['varc_' + str(i)] = int(data[line].split(' ')[7 + i])

            if op_c == 'Read_wait':
                #print 'RW'
                #print "line_c : " + str(line_c) + " host_c : " + str(host_c)
                matrix_rw[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_rw[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Read_exe':
                #print "RE"
                matrix_re[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_re[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Write_wait':
                #print "WW"
                matrix_ww[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_ww[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Write_exe':
                #print "WE"
                matrix_we[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_we[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Meta_wait':
                #print "MW"
                matrix_mw[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_mw[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Meta_exe':
                #print "ME"
                matrix_me[line_c][host_c * 9] = int(host_c)
                for j in range(0, 8):
                    matrix_me[line_c][host_c * 9 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]

            #print "Updating the head" #OK
            op_h = op_next
            for a in range(0, 8):
                locals()['varh_' + str(a)] = int(
                    data[line + 1].split(' ')[7 + a])

    #print matrix_rw
    np.savetxt("./csv_data/read_wait.csv", matrix_rw, fmt="%d", delimiter=",")
    np.savetxt("./csv_data/read_exe.csv", matrix_re, fmt="%d", delimiter=",")
    np.savetxt("./csv_data/write_wait.csv", matrix_ww, fmt="%d", delimiter=",")
    np.savetxt("./csv_data/write_exe.csv", matrix_we, fmt="%d", delimiter=",")
    np.savetxt("./csv_data/meta_wait.csv", matrix_mw, fmt="%d", delimiter=",")
    np.savetxt("./csv_data/meta_exe.csv", matrix_me, fmt="%d", delimiter=",")


def get_data(time_s, time_e):
    for mon in range(2, 3):
        if mon < 10:
            m = '0' + str(mon)
        else:
            m = str(mon)

    bandr = [([0] * 100000) for i in range(130)]
    bandw = [([0] * 100000) for i in range(130)]
    hostlist = []

    for index_item in range(25, 26):
        if index_item < 10:
            index = "2018." + m + "." + str(index_item)
            daytime = "2017-" + m + "-0" + str(index_item) + " " + "00:00:00"
            time_std = "2017-" + m + "-0" + str(index_item) + " " + "00:00:00"
        else:
            index = "2018." + m + "." + str(index_item)
            daytime = "2017-" + m + "-" + str(index_item) + " " + "00:00:00"
            time_std = "2017-" + m + "-" + str(index_item) + " " + "00:00:00"

        host_t = 91
        print index
        print daytime

        try:
            final_result = search(time_s, time_e, hostlist, index, host_t)
        except Exception as e:
            print e
            continue
        print "quert done"

        result = []
        queues = []
        for i in xrange(len(final_result[0])):
            host_ip = final_result[0][i]
            message = final_result[1][i]
            time = final_result[2][i]
            if 'queue' in message:
                queues.append(host_ip + ' ' + message + ' ' + time)
                continue
            result.append(host_ip + ' ' + message + ' ' + time)
        result.sort()
        queues.sort()
        print "Reshape and sort done..."
        #for r in result:
        #    print r
        #exit()
        return result, queues


if __name__ == '__main__':

    time_s = "2018-02-25 10:00:00"
    time_e = "2018-02-25 10:01:10"
    data, queues = get_data(time_s, time_e)
    print len(data)
    #print queues
    create_csv(data, time_s, time_e)
    deal_queue(queues, time_s, time_e)
