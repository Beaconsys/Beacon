from forwarding_each_all import search_le
from forwarding_each_all import search_gt
from forwarding_each_all import search
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv

timelines = 86400


def deal_queue(queues, daytime):

    time_a = datetime.datetime.strptime(
        daytime, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
    print queues[0]
    host_h = int(queues[0].split(' ')[0].split('.')[3]) - 17
    time_h = queues[0].split(' ')[1][1:] + ' ' + queues[0].split(' ')[2][0:-1]
    line_h = (datetime.datetime.strptime(time_h, "%Y-%m-%d %H:%M:%S") -
              time_a).seconds
    val_h = int(queues[0].split(' ')[7])
    #print queues[0].split(' ')

    #matrix = [[0 for i in range(128)] for i in range(timelines)]
    matrix = np.zeros((timelines, 128))
    matrix[line_h][host_h] = val_h

    #print "lendth: " + str(len(queues))
    file_line = len(queues)

    for line in range(1, file_line - 1):
        #print "Dealing line: " + str(line)
        time_c = queues[line].split(' ')[1][1:] + ' ' + queues[line].split(
            ' ')[2][0:-1]
        #time_next = queues[line + 1].split(' ')[1][1:] + ' ' + queues[line + 1].split(' ')[2][0:-1]
        line_c = (datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") -
                  time_a).seconds
        host_c = int(queues[line].split(' ')[0].split('.')[3]) - 17
        val_c = int(queues[line].split(' ')[7])
        if val_c > matrix[line_c][host_c]:
            matrix[line_c][host_c] = val_c

    print("start queue csv...")
    print matrix.max()
    #np.savetxt("./csv_data/queue"+str(daytime.split(' ')[0])+".csv", matrix, fmt = "%d", delimiter = ",")


def deal_latency(data_modify, daytime):
    #op: operation
    #c: current  h: head
    time_a = datetime.datetime.strptime(
        daytime, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)

    #data_modify=[]
    #for pj in data:
    #    if len(pj.split(' '))<15:
    #        continue
    #    else:
    #        data_modify.append(pj)

    x = data_modify[0].split(' ')
    host_h = int(x[0].split('.')[3]) - 17
    time_h = x[1][1:] + ' ' + x[2][:-1]
    line_h = (datetime.datetime.strptime(time_h, "%Y-%m-%d %H:%M:%S") -
              time_a).seconds
    op_h = x[5] + '_' + x[6][:-1]
    print op_h
    for i in range(8):
        locals()['varh_' + str(i)] = int(x[7 + i])

    #matrix_rw = [[0 for i in range(128 * 9)] for i in range(timelines)]
    #matrix_re = [[0 for i in range(128 * 9)] for i in range(timelines)]
    #matrix_ww = [[0 for i in range(128 * 9)] for i in range(timelines)]
    #matrix_we = [[0 for i in range(128 * 9)] for i in range(timelines)]
    #matrix_mw = [[0 for i in range(128 * 9)] for i in range(timelines)]
    #matrix_me = [[0 for i in range(128 * 9)] for i in range(timelines)]

    matrix_rw = np.zeros((timelines, 128 * 8))
    matrix_re = np.zeros((timelines, 128 * 8))
    matrix_ww = np.zeros((timelines, 128 * 8))
    matrix_we = np.zeros((timelines, 128 * 8))
    matrix_mw = np.zeros((timelines, 128 * 8))
    matrix_me = np.zeros((timelines, 128 * 8))

    file_line = len(data_modify)
    for line in range(1, file_line):
        #try:
        #    for i in range(8):
        #        locals()['varc_' + str(i)] = int(data[line-1].split(' ')[7 + i])
        #except Exception as e:
        #    print e
        try:
            y = data_modify[line].split(' ')
            op_c = y[5] + '_' + y[6][:-1]
            host_c = int(y[0].split('.')[3]) - 17
            time_c = y[1][1:] + ' ' + y[2][:-1]
        except Exception as e:
            print e
            print 111111, data_modify[line]
            continue
        #line_c = (datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") - time_a).seconds

        if op_h == op_c and time_h == time_c and host_h == host_c:
            continue
        else:
            for i in range(8):
                locals()['varc_' + str(i)] = int(
                    data_modify[line - 1].split(' ')[7 + i])

            if op_h == 'Read_wait':
                #print 'RW'
                for j in range(8):
                    matrix_rw[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Read_exe':
                #print "RE"
                for j in range(8):
                    matrix_re[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Write_wait':
                #print "WW"
                for j in range(8):
                    matrix_ww[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Write_exe':
                #print "WE"
                for j in range(8):
                    matrix_we[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Meta_wait':
                #print "MW"
                for j in range(8):
                    matrix_mw[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]
            elif op_h == 'Meta_exe':
                #print "ME"
                for j in range(8):
                    matrix_me[line_h][host_h * 8 + j] = locals()[
                        'varc_' + str(j)] - locals()['varh_' + str(j)]

            #print "Updating the head" #OK
            try:
                for a in range(8):
                    locals()['varh_' + str(a)] = int(y[7 + a])
            except Exception as e:
                print e
                print 222222, data_modify[line]
            op_h = op_c
            host_h = host_c
            time_h = time_c
            line_h = (datetime.datetime.strptime(time_c, "%Y-%m-%d %H:%M:%S") -
                      time_a).seconds

    #print matrix_rw
    print("start latency csv...")

    #ddir='./csv_data/'
    #path=[ddir+'read_wait.csv',ddir+'read_exe.csv',ddir+'write_wait.csv',ddir+'write_exe.csv',ddir+'meta_wait.csv',ddir+'meta_exe.csv']
    #for f in path:
    #    csvfile=file(f,'wb')
    #    writer=csv.writer(csvfile)
    #    for i in range(timelines):
    #        row=[]
    #        for r in matrix_rw[i]:
    #            row.append(r)
    #        writer.writerow(row)
    #    csvfile.close()
    finame = str(daytime.split(' ')[0])
    np.savetxt(
        "./csv_data/read_wait" + finame + ".csv",
        matrix_rw,
        fmt="%d",
        delimiter=",")
    np.savetxt(
        "./csv_data/read_exe" + finame + ".csv",
        matrix_re,
        fmt="%d",
        delimiter=",")
    np.savetxt(
        "./csv_data/write_wait" + finame + ".csv",
        matrix_ww,
        fmt="%d",
        delimiter=",")
    np.savetxt(
        "./csv_data/write_exe" + finame + ".csv",
        matrix_we,
        fmt="%d",
        delimiter=",")
    np.savetxt(
        "./csv_data/meta_wait" + finame + ".csv",
        matrix_mw,
        fmt="%d",
        delimiter=",")
    np.savetxt(
        "./csv_data/meta_exe" + finame + ".csv",
        matrix_me,
        fmt="%d",
        delimiter=",")


if __name__ == "__main__":
    time_s = '2018-03-14 11:35:00'
    time_e = '2018-03-14 11:44:00'
    hostlist = []
    for mon in range(2, 3):
        if mon < 10:
            m = '0' + str(mon)
        else:
            m = str(mon)
        for index_item in range(22, 29):
            bandr = [([0] * 100000) for i in range(130)]
            bandw = [([0] * 100000) for i in range(130)]
            if index_item < 10:
                index = "2018." + m + ".0" + str(index_item)
                daytime = "2018-" + m + "-0" + str(
                    index_item) + " " + "00:00:00"
                time_std = "2018-" + m + "-0" + str(
                    index_item) + " " + "20:00:00"
            else:
                index = "2018." + m + "." + str(index_item)
                daytime = "2018-" + m + "-" + str(
                    index_item) + " " + "00:00:00"
                time_std = "2018-" + m + "-" + str(
                    index_item) + " " + "20:00:00"
            host_t = 91
            print(index)
            print(daytime)
            #flag=0 debug flag=1 auto-run
            flag = 0
            if flag == 1:
                #auto serach,divide one day into two part
                try:
                    final_result = search_le(time_std, hostlist, index, host_t)
                except Exception as e:
                    print(e)
                    continue
                t1 = datetime.datetime.strptime(daytime, '%Y-%m-%d %H:%M:%S')
                result = []
                queue = []
                print("Query1 done...")
                for i in xrange(len(final_result[0])):
                    host_ip = final_result[0][i]
                    message = final_result[1][i]
                    time = final_result[2][i]
                    ss = host_ip + ' ' + message
                    if 'queue' in message:
                        if len(ss.split(' ')) == 8:
                            queue.append(ss)
                    else:
                        if len(ss.split(' ')) == 15:
                            result.append(host_ip + ' ' + message)
                try:
                    final_result = search_gt(time_std, hostlist, index, host_t)
                except Exception as e:
                    print(e)
                    continue
                print("Query2 done...")
            else:
                #########################################
                #debug
                try:
                    final_result = search(time_s, time_e, hostlist, index,
                                          host_t)
                except Exception as e:
                    print(e)
                    continue
                print("query done")
                result = []
                queue = []
#############################################
            for i in xrange(len(final_result[0])):
                host_ip = final_result[0][i]
                message = final_result[1][i]
                time = final_result[2][i]
                ss = host_ip + ' ' + message
                if 'queue' in message:
                    if len(ss.split(' ')) == 8:
                        queue.append(ss)
                else:
                    if len(ss.split(' ')) == 15:
                        result.append(host_ip + ' ' + message)
            result.sort()
            queue.sort()
            print("Reshape and sort done...")
            print("deal latency...")
            deal_latency(result, daytime)
            print("deal queue length...")
            deal_queue(queue, daytime)
