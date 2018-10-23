#coding:utf-8
import json
import numpy as np
import sys
import datetime
import scipy.io as sio
import matplotlib.pyplot as plt
from optparse import OptionParser
import csv
import exceptions
from time import clock
import socket

#sys.path.append("../query_script")
from job_ip_all import get_re_jobid as get_re_jobid_all
#sys.path.append("../ELK")
from time_to_sec import time_to_sec
import es_search
from savejob_jobid_modified import deal_csv, comput, compute_pre, compute_index, save_main
from deal_generator import deal_all_message, ost_deal_message, fwd_deal_message
from es_search_ost import search_interval as search_interval_ost
from es_search_fwd import search_interval as search_interval_fwd
from time_to_sec import time_to_sec_fast
size_ip = 50

IOBW_affective = 0.1

parser = OptionParser()

parser.add_option("-d", "--draw", default = False, action = "store_true",\
help = "Draw the figures", dest = "draw")

parser.add_option("-t", "--trace", default = False, action = "store_true", \
help = "Save the trace ", dest = "trace")

parser.add_option("-f", "--fd_info", default = False, action = "store_true", \
help = "Show the fd info", dest = "fd_info")

parser.add_option("-o", "--ost_info", default = False, action = "store_true", \
help = "Show the ost info", dest = "ost_info")

parser.add_option("-w", "--fwd_info", default = False, action = "store_true", \
help = "Show the forwarding info", dest = "fwd_info")

(options, args) = parser.parse_args()


def search_ost(file_list):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('20.0.2.17', 5000))
    except Exception as e:
        print e
    message = "/home/export/online1/swstorage/test.c,/home/export/online1/swstorage/taihu-io/*"
    message1 = "/home/export/online2/swstorage/mpiiotest/fs_test.x,/home/export/online2/swstorage/mpiiotest/data1/test50,/home/export/online2/swstorage/mpiiotest/data1/test51,/home/export/online2/swstorage/mpiiotest/data1/test63,/home/export/online2/swstorage/mpiiotest/data1/test62,/home/export/online2/swstorage/mpiiotest/data1/test61,/home/export/online2/swstorage/mpiiotest/data1/test60,/home/export/online2/swstorage/mpiiotest/data1/test49,/home/export/online2/swstorage/mpiiotest/data1/test48,/home/export/online2/swstorage/mpiiotest/data1/test10,/home/export/online2/swstorage/mpiiotest/data1/test11,/home/export/online2/swstorage/mpiiotest/data1/test8,/swstorage/mpiiotest/data1/test9,"
    print file_list
    s.send(message1 + "\n")
    str1 = s.recv(1024)
    s.close()
    array = str1.split(',')
    array_set = set(array)
    array = list(array_set)
    print len(array)
    array.sort()
    print array
    return array


def get_ost_data(start_time, end_time, ost_list, index, host):
    print ost_list
    ost_message = []
    ost_time = []
    ost_str = []
    for i in range(len(ost_list)):
        tmp = str(hex(int(ost_list[i])))[2:]
        if (len(tmp) == 1):
            ost_str.append('000' + tmp)
        elif (len(tmp) == 2):
            ost_str.append('00' + tmp)
        elif (len(tmp) == 3):
            ost_str.append('0' + tmp)

    print ost_str
    for index_tmp in index:
        #        try:
        ost_message_tmp, ost_time_tmp = search_interval_ost(
            start_time, end_time, ost_str, index_tmp, host)
        #        except Exception as e:
        #            print e
        ost_message += ost_message_tmp
        ost_time += ost_time_tmp
    print len(ost_message)
    print ost_message[0]
    time1 = start_time[:10] + ' ' + start_time[11:-5]
    time2 = end_time[:10] + ' ' + end_time[11:-5]
    bandr, bandw = ost_deal_message(ost_message, ost_time, time1, time2)
    return bandr, bandw


def get_fwd_data(start_time, end_time, fwd, ost_list, index, host):
    print ost_list
    ost_host = []
    ost_message = []
    ost_time = []
    ost_str = []
    for i in range(len(ost_list)):
        tmp = str(hex(int(ost_list[i])))[2:]
        if (len(tmp) == 1):
            ost_str.append('000' + tmp)
        elif (len(tmp) == 2):
            ost_str.append('00' + tmp)
        elif (len(tmp) == 3):
            ost_str.append('0' + tmp)

    print ost_str
    for index_tmp in index:
        ost_host_tmp, ost_message_tmp, ost_time_tmp = search_interval_fwd(
            start_time, end_time, fwd, ost_str, index_tmp, host)
        ost_host += ost_host_tmp
        ost_message += ost_message_tmp
        ost_time += ost_time_tmp
    print "fwd: %d message_length: %d" % (fwd, len(ost_message))
    print ost_host[0], ost_message[0], ost_time[0]
    time1 = start_time[:10] + ' ' + start_time[11:-5]
    time2 = end_time[:10] + ' ' + end_time[11:-5]

    bandr, bandw = fwd_deal_message(ost_message, ost_time, time1, time2)
    return bandr, bandw


def show_ost_data(ost_list, bandr, bandw):

    for ost in ost_list:
        print "Ost: %s \n" % ost
        print bandr[int(ost)]
        print bandw[int(ost)]


def draw_2d(x, y, tag):

    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.plot(x, 'r-')
    plt.plot(y, 'g-')
    #plt.plot([0, 35], [average, average], 'r-')
    #plt.xlabel('Runtime (day)', fontsize = 20)
    #plt.ylabel('IO_Time/Runtime ', fontsize = 20)
    plt.xlabel('time', fontsize=20)
    plt.ylabel(tag, fontsize=20)
    label = ["read", "write"]
    plt.legend(label, loc=1, ncol=1)
    plt.show()


def draw_d(x, tag):

    plt.xticks(fontsize=20)
    plt.plot(x, 'r-')
    #plt.plot([0, 35], [average, average], 'r-')
    #plt.xlabel('Runtime (day)', fontsize = 20)
    #plt.ylabel('IO_Time/Runtime ', fontsize = 20)
    plt.xlabel('time', fontsize=20)
    #    label = ["read"]
    #    plt.legend(label, loc = 1, ncol = 1)
    plt.show()


def save_tmp(resultr_band, resultw_band, resultr_iops, resultw_iops,
             resultr_open, resultw_close, pe_r, pe_w, tmp_file_name):
    f = open(tmp_file_name, "wb")
    for i in range(len(resultr_band)):
        if(abs(resultr_band[i]) > sys.float_info.epsilon or \
        abs(resultr_band[i]) > sys.float_info.epsilon or \
        abs(resultr_iops[i]) > sys.float_info.epsilon or \
        abs(resultw_iops[i]) > sys.float_info.epsilon or \
        abs(resultr_open[i]) > sys.float_info.epsilon or \
        abs(resultw_close[i]) > sys.float_info.epsilon or \
        abs(pe_r[i]) > sys.float_info.epsilon or \
        abs(pe_w[i]) > sys.float_info.epsilon):
            write_row = "%d %f %f %f %f %f %f %f %f \n"\
            %(i, resultr_band[i], resultw_band[i], resultr_iops[i], \
            resultw_iops[i], resultr_open[i], resultw_close[i], pe_r[i], pe_w[i])
            f.write(write_row)
        else:
            continue


def save_trace(result_message, result_host, trace_file_name):
    f = open(trace_file_name, "wb")
    for i in range(len(result_message)):
        write_row = "[Message]: %s [host]: %s\n" % (result_message[i],
                                                    result_host[i])
        f.write(write_row)


def read_csv(read_file):
    reader = csv.reader(read_file)
    read_results = []
    #    next(reader)
    for line in reader:
        read_results.append(line)
    read_file.close()
    return read_results


def show_IOBANDWIDTH(resultr, resultw, jobid):
    count_resultr = 0
    count_resultw = 0
    count_resultrw = 0
    sum_resultr = 0
    sum_resultw = 0
    max_resultr = max(resultr)
    max_resultw = max(resultw)
    for i in range(len(resultr)):
        #        if (abs(resultr[i]) > sys.float_info.epsilon):
        if (resultr[i] > IOBW_affective):
            #            if (resultr[i] < 1.0):
            #                print resultr[i]
            count_resultr += 1
            sum_resultr += resultr[i]
#        if (abs(resultw[i]) > sys.float_info.epsilon):
        if (resultw[i] > IOBW_affective):
            count_resultw += 1
            sum_resultw += resultw[i]


#        if(abs(resultr[i]) > sys.float_info.epsilon or \
#        abs(resultw[i]) > sys.float_info.epsilon):
        if(abs(resultr[i]) > IOBW_affective or \
        abs(resultw[i]) > IOBW_affective ):
            #            print i
            count_resultrw += 1
    average_resultr = 0.0
    average_resultw = 0.0
    print("count_IOBW_read  = %f " % (count_resultr))
    print("count_IOBW_write  = %f " % (count_resultw))
    print("count_IOBW_read_write = %f " % (count_resultrw))
    print("sum_IOBW_read  = %f MB " % (sum_resultr))
    print("sum_IOBW_write  = %f MB " % (sum_resultw))
    print("max_IOBW_read  = %f MB/s " % (max_resultr))
    print("max_IOBW_write  = %f MB/s " % (max_resultw))
    if (sum_resultr > sys.float_info.epsilon
            and count_resultr > sys.float_info.epsilon):
        average_resultr = sum_resultr / count_resultr
        print("average_IOBW_resultr = %f MB/s" % (average_resultr))
    if (sum_resultw > sys.float_info.epsilon
            and count_resultw > sys.float_info.epsilon):
        average_resultw = sum_resultw / count_resultw
        print("average_IOBW_resultw = %f MB/s" % (average_resultw))
    sum_resultrw = sum_resultr + sum_resultw
    if (sum_resultrw > sys.float_info.epsilon
            and count_resultrw > sys.float_info.epsilon):
        average_resultrw = sum_resultrw / count_resultrw
        print("average_IOBW_resultrw = %f MB/s" % (average_resultrw))


def show_IOPS(IOPS_r, IOPS_w, IOBW_r, IOBW_w, jobid):
    #Calculate the sum IOPS .
    count_IOPS_r = 0
    count_IOPS_w = 0
    count_IOPS_rw = 0
    count_IOPS_rw_all = 0
    sum_IOPS_r = 0
    sum_IOPS_w = 0
    for i in range(len(IOPS_r)):
        #        if (abs(IOPS_r[i]) > sys.float_info.epsilon):
        if (abs(IOPS_r[i]) > sys.float_info.epsilon \
            and IOBW_r[i] > IOBW_affective):
            count_IOPS_r += 1
            sum_IOPS_r += IOPS_r[i]


#        if (abs(IOPS_w[i]) > sys.float_info.epsilon):
        if (abs(IOPS_w[i]) > sys.float_info.epsilon \
            and IOBW_w[i] > IOBW_affective):
            count_IOPS_w += 1
            sum_IOPS_w += IOPS_w[i]
        if ((abs(IOPS_r[i]) > sys.float_info.epsilon and IOBW_r[i] > IOBW_affective) or \
        (abs(IOPS_w[i]) > sys.float_info.epsilon and IOBW_w[i] > IOBW_affective) ):
            count_IOPS_rw += 1
            #        if (IOBW_r[i] > 1.0 or \
            #        IOBW_w[i] > 1.0 or \
            #        abs(IOPS_r[i]) > sys.float_info.epsilon or \
            #        abs(IOPS_w[i]) > sys.float_info.epsilon):
            #        if (abs(IOBW_r[i]) > sys.float_info.epsilon or \
            #        abs(IOBW_w[i]) > sys.float_info.epsilon or \
            #        abs(IOPS_r[i]) > sys.float_info.epsilon or \
            #        abs(IOPS_w[i]) > sys.float_info.epsilon):
            count_IOPS_rw_all += 1
    print("count_IOPS_r = %f " % (count_IOPS_r))
    print("sum_IOPS_r = %f " % (sum_IOPS_r))
    print("count_IOPS_w = %f " % (count_IOPS_w))
    print("sum_IOPS_w = %f " % (sum_IOPS_w))
    average_IOPS_r = 0
    average_IOPS_w = 0
    if (sum_IOPS_r > sys.float_info.epsilon
            and count_IOPS_r > sys.float_info.epsilon):
        average_IOPS_r = sum_IOPS_r / count_IOPS_r
        print("average_IOPS_r = %f " % (average_IOPS_r))
    if (sum_IOPS_w > sys.float_info.epsilon
            and count_IOPS_r > sys.float_info.epsilon):
        average_IOPS_w = sum_IOPS_w / count_IOPS_w
        print("average_IOPS_w = %f " % (average_IOPS_w))


def show_MDS(MDS_o, MDS_c, jobid):
    #Calculate the sum MDS .
    count_MDS_o = 0
    count_MDS_c = 0
    count_MDS_oc = 0
    sum_MDS_o = 0
    sum_MDS_c = 0
    for i in range(len(MDS_o)):
        if (abs(MDS_o[i]) > sys.float_info.epsilon):
            count_MDS_o += 1
            sum_MDS_o += MDS_o[i]
        if (abs(MDS_c[i]) > sys.float_info.epsilon):
            count_MDS_c += 1
            sum_MDS_c += MDS_c[i]
        if (abs(MDS_o[i]) > sys.float_info.epsilon or \
        abs(MDS_c[i]) > sys.float_info.epsilon ):
            count_MDS_oc += 1

    print("count_MDS_o = %f " % (count_MDS_o))
    print("sum_MDS_o = %f " % (sum_MDS_o))
    print("count_MDS_c = %f " % (count_MDS_c))
    print("sum_MDS_c = %f " % (sum_MDS_c))
    average_MDS_o = 0
    average_MDS_c = 0
    if (sum_MDS_o > sys.float_info.epsilon
            and count_MDS_o > sys.float_info.epsilon):
        average_MDS_o = sum_MDS_o / count_MDS_o
        print("average_MDS_o = %f " % (average_MDS_o))
    if (sum_MDS_c > sys.float_info.epsilon
            and count_MDS_c > sys.float_info.epsilon):
        average_MDS_c = sum_MDS_c / count_MDS_c
        print("average_MDS_c = %f " % (average_MDS_c))


def show_process(dic, pa, min_time, max_time, jobid):
    host = dict()
    con = dict()
    count = 0
    for i in range(len(dic)):
        if not (host.has_key((dic[i][0], dic[i][1]))):
            host[(dic[i][0], dic[i][1])] = dic[i][2] / 1024.0
        else:
            host[(
                dic[i][0],
                dic[i][1])] = host[(dic[i][0], dic[i][1])] + dic[i][2] / 1024.0
    re = [0.0 for i in range(max_time - min_time + 5)]
    for key, value in host.items():
        if value > 50:
            re[key[1]] += 1
    count = 0
    #    for i in xrange(len(re)):
    #        if(re[i] > 0):
    #            count += 1
    #            print pa, " PE: ", re[i]

    max_PE = max(re)
    ave_PE = 0.0
    if (count > 0):
        ave_PE = sum(re) / count
    print pa, "max_PE: ", max_PE
    print pa, "ave_PE: ", ave_PE

    return re


def max_PE(PE_r, PE_w, jobid):
    if (len(PE_r) > 1):
        PE_r_max = max(PE_r)
    else:
        PE_r_max = 0
    if (len(PE_w) > 1):
        PE_w_max = max(PE_w)
    else:
        PE_w_max = 0


#def test_IOmode(resultr_band,resultw_band,resultr_iops,resultw_iops,resultr_open,\
#resultw_close, resultr_size, resultw_size, dictr, dictw, min_time, max_time):
#    title_IOmode = "collect_data/test"
#
#    IOBW_file_IO = file(title_IO+'/IOBW.csv','wb')
#    writer_IOBW_IO = csv.writer(IOBW_file_IO)
#    writer_IOBW_IO.writerow(['IOBW_r', 'IOBW_w'])
#
#    PER_file_IO = file(title_IO+'/PER.csv','wb')
#    writer_PER_IO = csv.writer(PER_file_IO)
#    writer_PER_IO.writerow(['max_PE_r'])
#
#    PEW_file_IO = file(title_IO+'/PEW.csv','wb')
#    writer_PEW_IO = csv.writer(PEW_file_IO)
#    writer_PEW_IO.writerow(['max_PE_w'])
#
#    MDS_file_IO = file(title_IO+'/MDS.csv','wb')
#    writer_MDS_IO = csv.writer(MDS_file_IO)
#    writer_MDS_IO.writerow(['MDS_r', 'MDS_w'])
#
#    saveIOBANDWIDTH(resultr_band, resultw_band, title_IOmode, jobid, \
#    program_name, corehour, min_time)
#    saveMDS(resultr_open,resultw_close,title_IOmode,jobid, \
#    program_name, corehour, min_time)
#    saveprocess(dictr,'r',title_IOmode,min_time,max_time,jobid, \
#    program_name, corehour)
#    saveprocess(dictw,'b',title_IOmode,min_time,max_time,jobid, \
#    program_name, corehour)


def test_save_main(starttime, endtime, jobid):

    title = 'test'
    title_IOmode = 'test_IO'
    title_IO = 'test_IO'

    IOBW_file = file(
        '../../results_job_data/collect_data/' + title + '/IOBW.csv', 'wb')
    writer_IOBW = csv.writer(IOBW_file)
    writer_IOBW.writerow(['program_name', 'jobID', 'start_time', 'end_time', \
    'sum_READ', 'sum_WRITE', 'count_r', 'count_w', 'count_rw', \
    'average_r', 'average_w'])

    IOPS_file = file(
        '../../results_job_data/collect_data/' + title + '/IOPS.csv', 'wb')
    writer_IOPS = csv.writer(IOPS_file)
    writer_IOPS.writerow(['program_name', 'jobID', 'start_time', 'end_time', \
    'sum_READ', 'sum_WRITE', 'count_r', 'count_w', 'count_rw', 'count_rw_all', \
    'average_r', 'average_w'])

    maxPE_file = file(
        '../../results_job_data/collect_data/' + title + '/maxPE.csv', 'wb')
    writer_maxPE = csv.writer(maxPE_file)
    writer_maxPE.writerow(['program_name', 'jobID', 'start_time', 'end_time', \
    'max_PE_r', 'max_PE_w'])

    MDS_file = file(
        '../../results_job_data/collect_data/' + title + '/MDS.csv', 'wb')
    writer_MDS = csv.writer(MDS_file)
    writer_MDS.writerow(['program_name', 'jobID', 'start_time', 'end_time', \
    'sum_OPEN', 'sum_CLOSE', 'count_o', 'count_c', 'count_oc', \
    'average_o', 'average_c'])

    size_r_file = file(
        '../../results_job_data/collect_data/' + title + '/SIZE_r.csv', 'wb')
    writer_r = csv.writer(size_r_file)
    writer_r.writerow(['Read_size', 'count', 'total_size'])

    size_w_file = file(
        '../../results_job_data/collect_data/' + title + '/SIZE_w.csv', 'wb')
    writer_w = csv.writer(size_w_file)
    writer_w.writerow(['Write_size', 'count', 'total_size'])

    IOBW_file_IO = file(
        '../../results_job_data/collect_data/' + title_IO + '/IOBW.csv', 'wb')
    writer_IOBW_IO = csv.writer(IOBW_file_IO)
    writer_IOBW_IO.writerow(['IOBW_r', 'IOBW_w'])

    PER_file_IO = file(
        '../../results_job_data/collect_data/' + title_IO + '/PER.csv', 'wb')
    writer_PER_IO = csv.writer(PER_file_IO)
    writer_PER_IO.writerow(['max_PE_r'])

    PEW_file_IO = file(
        '../../results_job_data/collect_data/' + title_IO + '/PEW.csv', 'wb')
    writer_PEW_IO = csv.writer(PEW_file_IO)
    writer_PEW_IO.writerow(['max_PE_w'])

    MDS_file_IO = file(
        '../../results_job_data/collect_data/' + title_IO + '/MDS.csv', 'wb')
    writer_MDS_IO = csv.writer(MDS_file_IO)
    writer_MDS_IO.writerow(['MDS_r', 'MDS_w'])

    file_name_file_IO = file(
        '../../results_job_data/collect_data/' + title_IO + '/file_name.csv',
        'wb')
    writer_file_name_IO = csv.writer(file_name_file_IO)
    writer_file_name_IO.writerow(['file_name_set', 'file_count'])

    jobid_abnormal_file = file(
        '../../results_job_data/collect_data/' + title + '/jobid_abnormal.csv',
        'wb')
    writer_jobid_abnormal = csv.writer(jobid_abnormal_file)
    try:
        save_main(starttime, endtime, jobid, 'cc', 1111, \
        title, title_IOmode, 1)
    except Exception as e:
        print e

    sys.exit()


def split_time(time1, time2, index):
    start_time = [(['00:00:00.000Z'] * 4) for i in range(len(index) - 2)]
    end_time = [(['00:00:00.000Z'] * 4) for i in range(len(index) - 2)]

    for i in xrange(1, len(index) - 1):
        x = (index[i]).split('.')
        start_day = x[0] + '-' + x[1] + '-' + x[2] + 'T'
        start_time[i - 1][0] = start_day + '00:00:00.000Z'
        end_time[i - 1][0] = start_day + '05:59:59.000Z'
        start_time[i - 1][1] = start_day + '06:00:00.000Z'
        end_time[i - 1][1] = start_day + '11:59:59.000Z'
        start_time[i - 1][2] = start_day + '12:00:00.000Z'
        end_time[i - 1][2] = start_day + '17:59:59.000Z'
        start_time[i - 1][3] = start_day + '18:00:00.000Z'
        end_time[i - 1][3] = start_day + '23:59:59.000Z'

    print start_time
    print end_time
    return start_time, end_time


def compute_pre_with_jobid(jobid):
    #    print time11, time12, jobid
    UTC = datetime.timedelta(hours=8)
    resu = []
    print jobid
    if int(jobid) == 0:
        resu = [[
            '00000000', 'quanji', 'quanji', '2018-05-21 14:00:00',
            '2018-05-21 15:00:00', 293L, 1L, 1L, ['0-40959']
        ]]
    else:
        resu = get_re_jobid_all(jobid)
    print resu
    for val in resu:
        ti = val[0] + " " + val[1] + " " + val[2]
        time21 = val[3]
        time22 = val[4]
        node = val[8]
        t21 = datetime.datetime.strptime(time21, '%Y-%m-%d %H:%M:%S')
        t22 = datetime.datetime.strptime(time22, '%Y-%m-%d %H:%M:%S')
        min_time = time_to_sec_fast(time21)
        max_time = time_to_sec_fast(time22)
        tt1 = str(t21 - UTC)
        tt2 = str(t22 - UTC)
        time1 = tt1[:10] + "T" + tt1[11:] + ".000Z"
        time2 = tt2[:10] + "T" + tt2[11:] + ".000Z"
        iplist = []
        fwd_list = dict()
    for no in node:
        a = no.split('-')
        try:
            int(a[0])
        except Exception:
            print a[0]
            print 'null node!!!'
            return
        if len(a) > 1:
            print a[0], a[1]
            for x in range(int(a[0]), int(a[1]) + 1):
                w2 = x // 1024
                w3 = (x - w2 * 1024) // 8
                w4 = x - w2 * 1024 - w3 * 8 + 1
                ip = "172." + str(w2) + "." + str(w3) + "." + str(w4)
                iplist.append(ip)

                fwd_no = x // 512
                if (fwd_no in fwd_list):
                    fwd_list[fwd_no].add(ip)
                else:
                    fwd_list[fwd_no] = set([ip])

        elif len(a) == 1:
            #print a[0]
            w2 = int(a[0]) // 1024
            w3 = (int(a[0]) - w2 * 1024) // 8
            w4 = int(a[0]) - w2 * 1024 - w3 * 8 + 1
            ip = "172." + str(w2) + "." + str(w3) + "." + str(w4)
            iplist.append(ip)

            fwd_no = int(a[0]) // 512
            if (fwd_no in fwd_list):
                fwd_list[fwd_no].add(ip)
            else:
                fwd_list[fwd_no] = set([ip])

    return time1, time2, iplist, min_time, max_time, fwd_list


def show_job_all(jobid):
    try:
        time1, time2, iplist, min_time, max_time, fwd_list \
        = compute_pre_with_jobid(jobid)
    except Exception as e:
        print e

    print time1
    print time2
    print min_time
    print max_time

    if (time1[8:10] == time2[8:10]):
        index = [time1[0:4] + "." + time1[5:7] + "." + time1[8:10]]
    else:
        index = compute_index(time1, time2)

    split_time_start, split_time_end = split_time(time1, time2, index)

    print "index: ", index
    count_ip = len(iplist) / size_ip
    remainder = len(iplist) % size_ip
    results_message = []
    results_host = []
    print "count_ip: ", count_ip
    print "remainder: ", remainder
    #    print len(index)

    try:
        for lnd in xrange(len(index)):
            print "Now search index: ", index[lnd]
            if (count_ip > 0):
                for c1 in xrange(count_ip):
                    print "Now search ip iteration: ", c1
                    try:
                        results_message_tmp, results_host_tmp = es_search.search(time1, time2,\
                        iplist[c1*size_ip:c1*size_ip+size_ip], index[lnd], 10)
                        results_message += results_message_tmp
                        results_host += results_host_tmp
                    except Exception as e:
                        print e
                    if (remainder > 0):
                        results_message_tmp, results_host_tmp = es_search.search(time1, time2,\
                        iplist[count_ip*size_ip:count_ip*size_ip + remainder], index[lnd], 1)
            else:
                results_message_tmp, results_host_tmp = es_search.search(time1, time2,\
                iplist, index[lnd], 1)
    except Exception as e:
        print e
        results_message_tmp = ""
        results_host_tmp = ""
        print "Warning, The ES index may be missing!!!!!"

    results_message += results_message_tmp
    results_host += results_host_tmp
    print 'message length: ', len(results_message)

    resultr_band,resultw_band,resultr_iops,resultw_iops,resultr_open,\
    resultw_close, resultr_size, resultw_size, dictr, dictw, file_count, \
    file_open, fd_info, fwd_file_map \
    = deal_all_message(results_message, results_host, min_time, max_time)
    print "JobID:", jobid
    print 'file_count: ', file_count
    show_IOBANDWIDTH(resultr_band, resultw_band, jobid)
    show_IOPS(resultr_iops, resultw_iops, resultr_band, resultw_band, jobid)
    show_MDS(resultr_open, resultw_close, jobid)
    pe_r = show_process(dictr, 'r', min_time, max_time, jobid)
    pe_w = show_process(dictw, 'b', min_time, max_time, jobid)
    file_open_count = [len(file_open[i]) for i in range(len(file_open))]

    if options.draw == True:
        draw_2d(resultr_band, resultw_band, 'IOBW')
        draw_2d(resultr_iops, resultw_iops, 'IOPS')
        draw_2d(pe_r, pe_w, 'PE')
        draw_d(file_open_count, 'Unique File Count')
        tmp_file_name = './results_job_data/tmp_csv/' + jobid + '.csv'
        print tmp_file_name
        save_tmp(resultr_band, resultw_band, resultr_iops, resultw_iops,
                 resultr_open, resultw_close, pe_r, pe_w, tmp_file_name)

    if options.trace == True:
        trace_file_name = './results_job_data/job_trace/' + jobid + '.csv'
        save_trace(results_message, results_host, trace_file_name)

    if options.fd_info == True:
        for fd in fd_info:
            print "[FD: %s] [filename: %s] [total_time: %d] \n\
            [sum_read_size: %f MB] [sum_write_size: %f MB] \n\
            [start_time: %s] [end_time: %s]"\
            %(fd, fd_info[fd]['file_name'], fd_info[fd]['total_time'], \
            fd_info[fd]['sum_read_size'], fd_info[fd]['sum_write_size'], \
            fd_info[fd]['start_time'], fd_info[fd]['end_time'])

    if options.ost_info == True:
        file_open_set = set()
        for i in range(len(file_open)):
            file_open_set |= file_open[i]
        if ('NULL' in file_open_set):
            file_open_set.remove('NULL')
        file_list = ""
        for file1 in file_open_set:
            file_list += file1
            file_list += ','
        ost_list = search_ost(file_list)
        if (len(ost_list) == 0):
            print "Files have been deleted."
        else:
            host = 90
            bandr, bandw = get_ost_data(time1, time2, ost_list, index, host)
            show_ost_data(ost_list, bandr, bandw)

    if options.fwd_info == True:
        for fwd in fwd_file_map:
            file_list = ''
            for file1 in fwd_file_map[fwd]:
                file_list += file1
                file_list += ','
            ost_list = search_ost(file_list)
            if (len(ost_list) == 0):
                print "Files have been deleted."
            else:
                host = 87
                bandr, bandw = get_fwd_data(time1, time2, fwd, ost_list, index,
                                            host)
                print "fwd: %s info: \n" % fwd
                print bandr
                print bandw


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "please input jobid e.g:6100000"
        sys.exit()
    else:
        print len(sys.argv)
    start_time0 = clock()
    jobid = sys.argv[1]
    #    test_save_main(time11, time12, jobid)
    show_job_all(jobid)
