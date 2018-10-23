import json
import numpy as np
import sys
import datetime
import scipy.io as sio
import matplotlib.pyplot as plt
import csv
import exceptions
from time import clock
from job_ip_all import get_re_jobid as get_re_jobid_all
from time_to_sec import time_to_sec
import es_search
from savejob_jobid_modified import deal_csv, comput, compute_pre, compute_index, save_main
from deal_generator import deal_all_message, ost_deal_message, fwd_deal_message
from es_search_ost import search_interval as search_interval_ost
from es_search_fwd import search_interval as search_interval_fwd
from time_to_sec import time_to_sec_fast

size_ip = 50
IOBW_affective = 0.1


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
        try:
            ost_message_tmp, ost_time_tmp = search_interval_ost(
                start_time, end_time, ost_str, index_tmp, host)
            ost_message += ost_message_tmp
            ost_time += ost_time_tmp
        except Exception as e:
            print e
        #ost_message += ost_message_tmp
        #ost_time += ost_time_tmp
    #print len(ost_message)
    #print ost_message[0]
    time1 = start_time[:10] + ' ' + start_time[11:-5]
    time2 = end_time[:10] + ' ' + end_time[11:-5]
    oslist, bandr, bandw = ost_deal_message(ost_message, ost_time, time1,
                                            time2)
    return bandr, bandw


def get_fwd_data(start_time, end_time, fwd, index, host):
    fwd_host = []
    fwd_message = []
    fwd_time = []
    st_str = ''
    for index_tmp in index:
        fwd_host_tmp, fwd_message_tmp, fwd_time_tmp = search_interval_fwd(
            start_time, end_time, fwd, st_str, index_tmp, host)
        for i in xrange(len(fwd_time_tmp)):
            if "cache" not in fwd_message_tmp[i]:
                fwd_host.append(fwd_host_tmp[i])
                fwd_message.append(fwd_message_tmp[i])
                fwd_time.append(fwd_time_tmp[i])
    time1 = start_time[:10] + ' ' + start_time[11:-5]
    time2 = end_time[:10] + ' ' + end_time[11:-5]

    ostlist, bandr, bandw = fwd_deal_message(fwd_message, fwd_time, time1,
                                             time2)
    return ostlist, bandr, bandw


def show_ost_data(ost_list, bandr, bandw):

    for ost in ost_list:
        print "Ost: %s \n" % ost
        print bandr[int(ost)]
        print bandw[int(ost)]


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


def show_IOBANDWIDTH(resultr, resultw):
    count_resultr = 0
    count_resultw = 0
    count_resultrw = 0
    sum_resultr = 0
    sum_resultw = 0
    max_resultr = max(resultr)
    max_resultw = max(resultw)
    resultrw = [0.0 for i in range(len(resultr))]
    for i in range(len(resultr)):
        #        if (abs(resultr[i]) > sys.float_info.epsilon):
        resultrw[i] = resultr[i] + resultw[i]
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
        if (abs(resultr[i]) > IOBW_affective
                or abs(resultw[i]) > IOBW_affective):
            #            print i
            count_resultrw += 1
    average_resultr = 0.0
    average_resultw = 0.0
    average_resultrw = 0.0
    #    print ("count_IOBW_read  = %f "%(count_resultr))
    #    print ("count_IOBW_write  = %f "%(count_resultw))
    #    print ("count_IOBW_read_write = %f "%(count_resultrw))
    #    print ("sum_IOBW_read  = %f MB "%(sum_resultr))
    #    print ("sum_IOBW_write  = %f MB "%(sum_resultw))
    #    print ("max_IOBW_read  = %f MB/s "%(max_resultr))
    #    print ("max_IOBW_write  = %f MB/s "%(max_resultw))
    if (sum_resultr > sys.float_info.epsilon
            and count_resultr > sys.float_info.epsilon):
        average_resultr = sum_resultr / count_resultr
#        print ("average_IOBW_resultr = %f MB/s"%(average_resultr))
    if (sum_resultw > sys.float_info.epsilon
            and count_resultw > sys.float_info.epsilon):
        average_resultw = sum_resultw / count_resultw
#        print ("average_IOBW_resultw = %f MB/s"%(average_resultw))
    sum_resultrw = sum_resultr + sum_resultw
    if (sum_resultrw > sys.float_info.epsilon
            and count_resultrw > sys.float_info.epsilon):
        average_resultrw = sum_resultrw / count_resultrw


#        print ("average_IOBW_resultrw = %f MB/s"%(average_resultrw))
    max_resultrw = max(resultrw)
    #    return average_resultr,max_resultr,average_resultw,max_resultw,average_resultrw,max_resultrw
    return average_resultrw, max_resultrw, sum_resultrw


def compute_pre_with_jobid(jobid):
    fwd_map = [
        81, 82, 105, 85, 87, 88, 89, 90, 93, 136, 97, 99, 101, 103, 91, 92,
        130, 131, 140, 133, 134, 135, 96, 63, 100, 102, 128, 129, 104, 137, 56,
        86, 83, 95, 30, 127, 141, 142, 143, 144, 107, 108, 109, 110, 111, 112,
        113, 55, 121, 116, 117, 118, 119, 120, 122, 94, 124, 125, 138, 139, 23,
        24, 25, 26, 27, 28, 29, 44, 31, 45, 33, 34, 35, 36, 37, 38, 39, 40, 41,
        42, 126, 20, 43
    ]
    UTC = datetime.timedelta(hours=8)
    resu = []
    resu = get_re_jobid_all(jobid)
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
                if (fwd_map[fwd_no] in fwd_list):
                    fwd_list[fwd_map[fwd_no]].add(ip)
                else:
                    fwd_list[fwd_map[fwd_no]] = set([ip])
        elif len(a) == 1:
            #print a[0]
            w2 = int(a[0]) // 1024
            w3 = (int(a[0]) - w2 * 1024) // 8
            w4 = int(a[0]) - w2 * 1024 - w3 * 8 + 1
            ip = "172." + str(w2) + "." + str(w3) + "." + str(w4)
            iplist.append(ip)
            fwd_no = int(a[0]) // 512
            if (fwd_map[fwd_no] in fwd_list):
                fwd_list[fwd_map[fwd_no]].add(ip)
            else:
                fwd_list[fwd_map[fwd_no]] = set([ip])
    return time1, time2, iplist, min_time, max_time, fwd_list


def detect(jobid):
    try:
        time1, time2, iplist, min_time, max_time, fwdlist = compute_pre_with_jobid(
            jobid)
    except Exception as e:
        print e
    if (time1[8:10] == time2[8:10]):
        index = [time1[0:4] + "." + time1[5:7] + "." + time1[8:10]]
    else:
        index = compute_index(time1, time2)
    #split_time_start, split_time_end = split_time(time1, time2, index)
    print "index: ", index, " time1:", time1, " time2:", time2
    job_cmp = dict()
    for r in fwdlist:
        iplist = list(fwdlist[r])
        count_ip = len(iplist) / size_ip
        remainder = len(iplist) % size_ip
        results_message = []
        results_host = []
        print "Now fwd: ", r, " Now iplist: ", iplist
        try:
            for lnd in xrange(len(index)):
                print "Now search index: ", index[lnd]
                if (count_ip > 0):
                    print "count_ip ", count_ip
                    for c1 in xrange(count_ip):
                        print "Now search ip iteration: ", c1
                        try:
                            results_message_tmp, results_host_tmp = es_search.search(
                                time1, time2,
                                iplist[c1 * size_ip:c1 * size_ip + size_ip],
                                index[lnd], 10)
                            results_message += results_message_tmp
                            results_host += results_host_tmp
                        except Exception as e:
                            print e
                    if (remainder > 0):
                        results_message_tmp, results_host_tmp = es_search.search(
                            time1, time2,
                            iplist[count_ip * size_ip:count_ip * size_ip +
                                   remainder], index[lnd], 1)
                else:
                    results_message_tmp, results_host_tmp = es_search.search(
                        time1, time2, iplist, index[lnd], 1)
        except Exception as e:
            print e
            results_message_tmp = ""
            results_host_tmp = ""
            print "Warning, The ES index may be missing!!!!!"

        results_message += results_message_tmp
        results_host += results_host_tmp
        print 'message length: ', len(results_message)

        (resultr_band, resultw_band, resultr_iops, resultw_iops, resultr_open,
         resultw_close, resultr_size, resultw_size, dictr, dictw, file_count,
         file_open1, fd_info, fwd_file_map1) = deal_all_message(
             results_message, results_host, min_time, max_time)
        b1, b2, b3 = show_IOBANDWIDTH(resultr_band, resultw_band)
        job_cmp[r] = [b1, b2, b3]
    print "begin fwd search..."
    print "fwdlist: ", fwdlist.keys()

    print time1, time2
    time1_f = time1
    time2_f = time2
    job_fwd = dict()
    host = 87
    ostlist = []
    fwd_band_sum = 0.0
    fwd_volume_sum = 0.0
    fwd_count = 0
    for fwd in fwdlist:
        #print "fwd: ",fwd
        fwd_count += 1
        ostlist1, fwd_bandr, fwd_bandw = get_fwd_data(time1, time2, fwd, index,
                                                      host)
        b1, b2, b3 = show_IOBANDWIDTH(fwd_bandr, fwd_bandw)
        fwd_band_sum += b2
        fwd_volume_sum += b3
        job_fwd[fwd] = [b1, b2, b3]
        for ostid in ostlist1:
            if ostid not in ostlist:
                ostlist.append(ostid)
    fwdlist_issue_next = []
    for fwd in fwdlist:
        if job_fwd[fwd][0] < (
                fwd_band_sum / fwd_count / 2) and job_fwd[fwd][1] < (
                    fwd_band_sum / fwd_count / 2) and (
                        fwd_volume_sum / 5 * 3 / fwd_count < job_fwd[fwd][2]):
            fwdlist_issue_next.append(fwd)
    print "fwd anomaly check: ", fwdlist_issue_next
    for ti in [1, 4, 12, 96]:
        fwdlist_issue = []
        for r in fwdlist_issue_next:
            fwdlist_issue.append(r)
        time1_std = time1_f[:10] + ' ' + time1_f[11:-5]
        time2_std = time2_f[:10] + ' ' + time2_f[11:-5]
        t1 = datetime.datetime.strptime(time1_std, '%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.strptime(time2_std, '%Y-%m-%d %H:%M:%S')
        time_interval = datetime.timedelta(hours=ti)
        tt1 = t1 - time_interval
        tt2 = t2 + time_interval
        time1_f = str(tt1)[:10] + 'T' + str(tt1)[11:] + '.000Z'
        time2_f = str(tt2)[:10] + 'T' + str(tt2)[11:] + '.000Z'
        fwd_band_sum = 0.0
        fwd_volume_sum = 0.0
        fwd_count = 0
        for fwd in fwdlist_issue:
            #print "fwd: ",fwd
            fwd_count += 1
            ostlist1, fwd_bandr, fwd_bandw = get_fwd_data(
                time1_f, time2_f, fwd, index, host)
            b1, b2, b3 = show_IOBANDWIDTH(fwd_bandr, fwd_bandw)
            fwd_band_sum += b2
            fwd_volume_sum += b3
            job_fwd[fwd] = [b1, b2, b3]
            for ostid in ostlist1:
                if ostid not in ostlist:
                    ostlist.append(ostid)

        fwdlist_issue_next = []
        for fwd in fwdlist_issue:
            if job_fwd[fwd][0] < (fwd_band_sum / fwd_count / 2) and job_fwd[
                    fwd][1] < (fwd_band_sum / fwd_count / 2) and (
                        fwd_volume_sum / 5 * 3 / fwd_count < job_fwd[fwd][2]):
                fwdlist_issue_next.append(fwd)
        print "Anomaly time: ", ti, " ", list(
            set(fwdlist_issue).difference(set(fwdlist_issue_next)))

    print "begin OST search..."
    print "OSTlist: ", ostlist
    job_ost = dict()
    host = 88
    time1_o = time1
    time2_o = time2
    ost_bandr, ost_bandw = get_ost_data(time1, time2, ostlist, index, host)
    ost_band_sum = 0.0
    ost_volume_sum = 0.0
    ost_count = 0
    for ostid in ostlist:
        ost_count += 1
        tmpr = []
        tmpw = []
        for j in range(len(ost_bandr[0])):
            tmpr.append(ost_bandr[ostid][j])
            tmpw.append(ost_bandw[ostid][j])
        b1, b2, b3 = show_IOBANDWIDTH(tmpr, tmpw)
        ost_band_sum += b2
        ost_volume_sum += b3
        job_ost[ostid] = [b1, b2, b3]
    ostlist_issue_next = []
    for ostid in ostlist:
        try:
            if job_ost[ostid][0] < (
                    ost_band_sum / ost_count / 2
            ) and job_ost[ostid][1] < (ost_band_sum / ost_count / 2) and (
                    ost_volume_sum / 5 * 3 / ost_count < job_ost[ostid][2]):
                ostlist_issue_next.append(ostid)
        except Exception as e:
            print e

    print "ost anomaly check: ", ostlist_issue_next
    for ti in [1, 4, 12, 96]:
        print "begin time: ", ti
        ostlist_issue = []
        for r in ostlist_issue_next:
            ostlist_issue.append(r)
        if len(ostlist_issue) < 1:
            break
        time1_std = time1_o[:10] + ' ' + time1_o[11:-5]
        time2_std = time2_o[:10] + ' ' + time2_o[11:-5]
        t1 = datetime.datetime.strptime(time1_std, '%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.strptime(time2_std, '%Y-%m-%d %H:%M:%S')
        time_interval = datetime.timedelta(hours=ti)
        tt1 = t1 - time_interval
        tt2 = t2 + time_interval
        time1_o = str(tt1)[:10] + 'T' + str(tt1)[11:] + '.000Z'
        time2_o = str(tt2)[:10] + 'T' + str(tt2)[11:] + '.000Z'

        ost_bandr, ost_bandw = get_ost_data(time1_o, time2_o, ostlist_issue,
                                            index, host)
        ost_band_sum = 0.0
        ost_volume_sum = 0.0
        ost_count = 0
        for ostid in ostlist_issue:
            #print "fwd: ",fwd
            ost_count += 1
            tmpr = []
            tmpw = []
            for j in range(len(ost_bandr[0])):
                tmpr.append(ost_bandr[ostid][j])
                tmpw.append(ost_bandw[ostid][j])
            b1, b2, b3 = show_IOBANDWIDTH(tmpr, tmpw)
            ost_band_sum += b2
            ost_volume_sum += b3
            job_ost[ostid] = [b1, b2, b3]

        ostlist_issue_next = []
        for ostid in ostlist_issue:
            try:
                if job_ost[ostid][0] < (
                        ost_band_sum / ost_count / 2) and job_ost[ostid][1] < (
                            ost_band_sum / ost_count / 2) and (
                                ost_volume_sum / 5 * 3 / ost_count <
                                job_ost[ostid][2]):
                    ostlist_issue_next.append(ostid)
            except Exception as e:
                print e
        print "Anomaly time: ", ti, " ", list(
            set(ostlist_issue).difference(set(ostlist_issue_next)))


if __name__ == "__main__":
    if (len(sys.argv) < 1):
        print "please input jobid e.g:6100000"
        sys.exit()
    start_time0 = clock()
    jobid = sys.argv[1]
    print jobid
    detect(jobid)
