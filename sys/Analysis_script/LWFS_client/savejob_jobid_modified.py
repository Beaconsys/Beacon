# uncompyle6 version 3.1.2
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Aug  4 2017, 00:39:18)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-16)]
# Embedded file name: /home/export/mount_test/swstorage/taihu-io/job_query_script/savejob_jobid_modified.py
# Compiled at: 2018-03-15 18:49:42
import json, numpy as np, sys
sys.path.insert(0, '../../job')
sys.path.append('../query_script')
from job_ip_all import get_re_jobid
from time_to_sec import time_to_sec_fast
import csv, exceptions, es_search, threading, datetime
from deal_generator import deal_all_message
import gc
node_count = 50
IOBW_affective = 0.1
length = 5000


def save_all(jobID, CNC, runtime, resultr_band, resultw_band, resultr_iops,
             resultw_iops, resultr_open, resultw_close, pe_r, pe_w,
             tmp_file_name):
    f = open(tmp_file_name, 'wb')
    for i in range(len(resultr_band)):
        if abs(resultr_band[i]) > sys.float_info.epsilon or abs(
                resultr_band[i]) > sys.float_info.epsilon or abs(
                    resultr_iops[i]) > sys.float_info.epsilon or abs(
                        resultw_iops[i]) > sys.float_info.epsilon or abs(
                            resultr_open[i]) > sys.float_info.epsilon or abs(
                                resultw_close[i]
                            ) > sys.float_info.epsilon or abs(
                                pe_r[i]) > sys.float_info.epsilon or abs(
                                    pe_w[i]) > sys.float_info.epsilon:
            write_row = '%d :%f %f %f %f %f %f %f %f \n' % (
                i, resultr_band[i], resultw_band[i], resultr_iops[i],
                resultw_iops[i], resultr_open[i], resultw_close[i], pe_r[i],
                pe_w[i])
            f.write(write_row)
        else:
            continue


def read_csv(read_file):
    reader = csv.reader(read_file)
    read_results = []
    for line in reader:
        read_results.append(line)

    read_file.close()
    return read_results


def deal_csv(results_message, results_host, min_time, max_time, time1, time2):
    global compression_count
    global no_count
    resultr = np.array([0.0 for i in range(max_time - min_time + 5)])
    resultw = np.array([0.0 for i in range(max_time - min_time + 5)])
    result_open = np.array([0 for i in range(max_time - min_time + 5)])
    result_close = np.array([0 for i in range(max_time - min_time + 5)])
    resultr_ops = np.array([0 for i in range(max_time - min_time + 5)])
    resultw_ops = np.array([0 for i in range(max_time - min_time + 5)])
    resultr_size = []
    resultw_size = []
    dictr = []
    dictw = []
    compression_count = 0
    no_count = 0
    index_cc = 0
    for i in xrange(len(results_message)):
        x = results_message[i].split()
        time = x[0] + ' ' + x[1]
        c_time = time[1:-1]
        ke = x[6]
        kee = x[3]
        if ke == 'OPEN':
            try:
                ctime = time_to_sec_fast(c_time)
                index = ctime - min_time + 1
                result_open[index] += 1
                no_count += 1
                compression_count += 1
            except Exception as e:
                c1 = 1

        elif ke == 'RELEASE':
            try:
                ctime = time_to_sec_fast(c_time)
                index = ctime - min_time + 1
                result_close[index] += 1
                no_count += 1
                compression_count += 1
            except Exception as e:
                c1 = 1

        elif kee == 'READ':
            try:
                if 'offset' not in results_message[i]:
                    offset_judge = 1
                    ip = results_host[i]
                    size = x[4].split('=')[1]
                    op_count = int(x[5].split('=')[1])
                    sumsize = int(size)
                    ctime = time_to_sec_fast(c_time)
                    index = ctime - min_time + 1
                    resultr[index] += sumsize / 1048576.0
                    resultr_ops[index] += op_count
                    resultr_size.append([sumsize / op_count * 1.0, op_count])
                else:
                    offset_judge = 2
                    ip = results_host[i]
                    size = int(x[5].split('=')[1])
                    op_count = int(x[7].split('=')[1])
                    sumsize = int(size) * op_count
                    ctime = time_to_sec_fast(c_time)
                    index = ctime - min_time + 1
                    resultr[index] += sumsize / 1048576.0
                    resultr_ops[index] += op_count
                    resultr_size.append([size, op_count])
                dictr.append([ip, index, sumsize, op_count])
                no_count += op_count
                compression_count += 1
            except Exception as e:
                c1 = 1

        elif kee == 'WRITE':
            try:
                if 'offset' not in results_message[i]:
                    offset_judge = 1
                    ip = results_host[i]
                    size = x[4].split('=')[1]
                    op_count = int(x[5].split('=')[1])
                    sumsize = int(size)
                    ctime = time_to_sec_fast(c_time)
                    index = ctime - min_time + 1
                    resultw[index] += sumsize / 1048576.0
                    resultw_ops[index] += op_count
                    resultw_size.append([sumsize / op_count * 1.0, op_count])
                else:
                    offset_judge = 2
                    ip = results_host[i]
                    size = int(x[5].split('=')[1])
                    op_count = int(x[7].split('=')[1])
                    sumsize = int(size) * op_count
                    ctime = time_to_sec_fast(c_time)
                    index = ctime - min_time + 1
                    resultw[index] += sumsize / 1048576.0
                    resultw_ops[index] += op_count
                    resultw_size.append([size, op_count])
                dictw.append([ip, index, sumsize, op_count])
                no_count += op_count
                compression_count += 1
            except Exception as e:
                c1 = 1

    return (resultr, resultw, resultr_ops, resultw_ops, result_open,
            result_close, resultr_size, resultw_size, dictr, dictw)


def compute_month_day(month):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        month_day = 31
    else:
        if month == 4 or month == 6 or month == 9 or month == 11:
            month_day = 30
        else:
            month_day = 28
    return month_day


def compute_index(starttime, endtime):
    time_start = starttime[0:4] + '.' + starttime[5:7] + '.' + starttime[8:10]
    time_end = endtime[0:4] + '.' + endtime[5:7] + '.' + endtime[8:10]
    start_month = int(starttime[5:7])
    end_month = int(endtime[5:7])
    start_day = int(starttime[8:10])
    end_day = int(endtime[8:10])
    month_count = end_month - start_month
    day_count = end_day - start_day
    index = []
    if month_count == 0:
        for i in xrange(day_count + 1):
            if start_day + i < 10:
                index.append(starttime[0:4] + '.' + starttime[5:7] + '.0' +
                             str(start_day + i))
            else:
                index.append(starttime[0:4] + '.' + starttime[5:7] + '.' +
                             str(start_day + i))

    else:
        if month_count == 1:
            start_month_day = compute_month_day(start_month)
            for month_i in xrange(start_day, start_month_day + 1):
                if month_i < 10:
                    index.append(starttime[0:4] + '.' + starttime[5:7] + '.0' +
                                 str(month_i))
                else:
                    index.append(starttime[0:4] + '.' + starttime[5:7] + '.' +
                                 str(month_i))

            for month_j in xrange(1, end_day + 1):
                if month_j < 10:
                    index.append(endtime[0:4] + '.' + endtime[5:7] + '.0' +
                                 str(month_j))
                else:
                    index.append(endtime[0:4] + '.' + endtime[5:7] + '.' +
                                 str(month_j))

    return index


def comput(time1, time2, iplist, cache_file):
    pp = 0
    cache_writer = csv.writer(cache_file)
    q0 = RangeQuery(
        qrange=ESRange('@timestamp', from_value=time1, to_value=time2))
    q3 = MatchQuery('message', 'OPEN')
    q4 = MatchQuery('message', 'RELEASE')
    q6 = MatchQuery('message', 'READ')
    q7 = MatchQuery('message', 'WRITE')
    q5 = BoolQuery(should=[q3, q4, q6, q7])
    for i in range(len(iplist)):
        pp += 1
        if pp == 1:
            q1 = MatchQuery('host', iplist[i])
        else:
            q2 = MatchQuery('host', iplist[i])
            q1 = BoolQuery(should=[q1, q2])
        if pp >= 50:
            pp = 0
            query = BoolQuery(must=[q1, q0, q5])
            search = Search(query, fields=['host'])
            results = conn.search(search)
            iterations = len(results) / length + 1
            if len(results) > 0:
                print 'iterations= ', iterations, 'alllength= ', len(results)
            for k in range(0, iterations):
                search = Search(
                    query,
                    fields=['message', 'host'],
                    size=length,
                    start=k * length)
                results = conn.search(search)
                for r in results:
                    cache_writer.writerow([str(r)])

    if pp > 0:
        query = BoolQuery(must=[q1, q0, q5])
        search = Search(query, fields=['host'])
        results = conn.search(search)
        iterations = len(results) / length + 1
        if len(results) > 0:
            print 'iterations= ', iterations, 'alllength= ', len(results)
        for k in range(0, iterations):
            search = Search(
                query,
                fields=['message', 'host'],
                size=length,
                start=k * length)
            results = conn.search(search)
            start_time2 = clock()
            for r in results:
                cache_writer.writerow([str(r)])

    cache_file.close()


def sum_IOBANDWIDTH(resultr, resultw):
    count_resultr = 0
    count_resultw = 0
    count_resultrw = 0
    sum_resultr = 0
    sum_resultw = 0
    for i in range(len(resultr)):
        if abs(resultr[i]) > IOBW_affective:
            count_resultr += 1
            sum_resultr += resultr[i]
        if abs(resultw[i]) > IOBW_affective:
            count_resultw += 1
            sum_resultw += resultw[i]
        if abs(resultr[i]) > IOBW_affective or abs(
                resultw[i]) > IOBW_affective:
            count_resultrw += 1

    average_resultr = 0.0
    average_resultw = 0.0
    if sum_resultr > sys.float_info.epsilon and count_resultr > sys.float_info.epsilon:
        average_resultr = sum_resultr / count_resultr
    if sum_resultw > sys.float_info.epsilon and count_resultw > sys.float_info.epsilon:
        average_resultw = sum_resultw / count_resultw
    return (sum_resultr, sum_resultw, average_resultr, average_resultw,
            count_resultr, count_resultw, count_resultrw, average_resultr,
            average_resultw)


def sum_IOPS(IOPS_r, IOPS_w, IOBW_r, IOBW_w):
    count_IOPS_r = 0
    count_IOPS_w = 0
    count_IOPS_rw = 0
    count_IOPS_rw_all = 0
    sum_IOPS_r = 0
    sum_IOPS_w = 0
    for i in range(len(IOPS_r)):
        if abs(IOPS_r[i]
               ) > sys.float_info.epsilon and IOBW_r[i] > IOBW_affective:
            count_IOPS_r += 1
            sum_IOPS_r += IOPS_r[i]
        if abs(IOPS_w[i]
               ) > sys.float_info.epsilon and IOBW_w[i] > IOBW_affective:
            count_IOPS_w += 1
            sum_IOPS_w += IOPS_w[i]
        if abs(IOPS_r[i]) > sys.float_info.epsilon and IOBW_r[
                i] > IOBW_affective or abs(
                    IOPS_w[i]
                ) > sys.float_info.epsilon and IOBW_w[i] > IOBW_affective:
            count_IOPS_rw += 1
            count_IOPS_rw_all += 1

    average_IOPS_r = 0
    average_IOPS_w = 0
    if sum_IOPS_r > sys.float_info.epsilon and count_IOPS_r > sys.float_info.epsilon:
        average_IOPS_r = sum_IOPS_r / count_IOPS_r
    if sum_IOPS_w > sys.float_info.epsilon and count_IOPS_r > sys.float_info.epsilon:
        average_IOPS_w = sum_IOPS_w / count_IOPS_w
    return (sum_IOPS_r, sum_IOPS_w, count_IOPS_r, count_IOPS_w, count_IOPS_rw,
            count_IOPS_rw_all, average_IOPS_r, average_IOPS_w)


def sum_MDS(MDS_o, MDS_c):
    count_MDS_o = 0
    count_MDS_c = 0
    count_MDS_oc = 0
    sum_MDS_o = 0
    sum_MDS_c = 0
    for i in range(len(MDS_o)):
        if abs(MDS_o[i]) > sys.float_info.epsilon:
            count_MDS_o += 1
            sum_MDS_o += MDS_o[i]
        if abs(MDS_c[i]) > sys.float_info.epsilon:
            count_MDS_c += 1
            sum_MDS_c += MDS_c[i]
        if abs(MDS_o[i]) > sys.float_info.epsilon or abs(
                MDS_c[i]) > sys.float_info.epsilon:
            count_MDS_oc += 1

    average_MDS_o = 0
    average_MDS_c = 0
    if sum_MDS_o > sys.float_info.epsilon and count_MDS_o > sys.float_info.epsilon:
        average_MDS_o = sum_MDS_o / count_MDS_o
    if sum_MDS_c > sys.float_info.epsilon and count_MDS_c > sys.float_info.epsilon:
        average_MDS_c = sum_MDS_c / count_MDS_c
    return (sum_MDS_o, sum_MDS_c, count_MDS_o, count_MDS_c, count_MDS_oc,
            average_MDS_o, average_MDS_c)


def sum_process(dic, pa, min_time, max_time):
    host = dict()
    con = dict()
    count = 0
    for i in range(len(dic)):
        if not host.has_key((dic[i][0], dic[i][1])):
            host[(dic[i][0], dic[i][1])] = dic[i][2] / 1024.0
        else:
            host[(
                dic[i][0],
                dic[i][1])] = host[(dic[i][0], dic[i][1])] + dic[i][2] / 1024.0

    re = [0.0 for i in range(max_time - min_time + 5)]
    for key, value in host.items():
        if value > 50:
            re[key[1]] += 1

    max_PE = max(re)
    return max_PE


def max_PE(PE_r, PE_w, jobid):
    if len(PE_r) > 1:
        PE_r_max = max(PE_r)
    else:
        PE_r_max = 0
    if len(PE_w) > 1:
        PE_w_max = max(PE_w)
    else:
        PE_w_max = 0


def saveIOBANDWIDTH(resultr, resultw, title, jobid, program_name, corehour,
                    min_time):
    for i in range(len(resultr)):
        resultr[i] = resultr[i]
        resultw[i] = resultw[i]

    csvfile = file(
        '../../results_job_data/collect_data/' + title + '/IOBW.csv', 'ab')
    writer = csv.writer(csvfile)
    date = []
    allr = 0.0
    allw = 0.0
    writer.writerow([
        'program_name and jobID ',
        str(program_name),
        str(jobid),
        str(corehour),
        str(min_time)
    ])
    for xu in xrange(len(resultr)):
        if abs(resultr[xu]) > sys.float_info.epsilon or abs(
                resultw[xu]) > sys.float_info.epsilon:
            date.append((str(xu), str(resultr[xu]), str(resultw[xu])))
            allr += resultr[xu]
            allw += resultw[xu]
        else:
            continue

    writer.writerows(date)
    csvfile.close()


def saveIOPS(resultr, resultw, title, jobid, program_name, corehour, min_time):
    csvfile = file('../date/' + title + '_IOPS.csv', 'ab')
    writer = csv.writer(csvfile)
    date = []
    writer.writerow([
        'program_name and jobID ',
        str(program_name),
        str(jobid),
        str(corehour),
        str(min_time)
    ])
    for xu in xrange(len(resultr)):
        if abs(resultr[xu]) > sys.float_info.epsilon or abs(
                resultw[xu]) > sys.float_info.epsilon:
            date.append((str(xu), str(resultr[xu]), str(resultw[xu])))
        else:
            continue

    writer.writerows(date)
    csvfile.close()


def saveMDS(resultr, resultw, title, jobid, program_name, corehour, min_time):
    csvfile = file('../../results_job_data/collect_data/' + title + '/MDS.csv',
                   'ab')
    writer = csv.writer(csvfile)
    date = []
    writer.writerow([
        'program_name and jobID ',
        str(program_name),
        str(jobid),
        str(corehour),
        str(min_time)
    ])
    for xu in xrange(len(resultr)):
        if abs(resultr[xu]) > sys.float_info.epsilon or abs(
                resultw[xu]) > sys.float_info.epsilon:
            date.append((str(xu), str(resultr[xu]), str(resultw[xu])))
        else:
            continue

    writer.writerows(date)
    csvfile.close()


def savefilename(file_set_open, title, jobid, program_name, corehour,
                 min_time):
    csvfile = file(
        '../../results_job_data/collect_data/' + title + '/file_name.csv',
        'ab')
    writer = csv.writer(csvfile)
    data = []
    writer.writerow([
        'program_name and jobID ',
        str(program_name),
        str(jobid),
        str(corehour),
        str(min_time)
    ])
    for xu in xrange(len(file_set_open)):
        if len(file_set_open[xu]) > 0:
            data.append((str(xu), str(file_set_open[xu]),
                         str(len(file_set_open[xu]))))
        else:
            continue

    writer.writerows(data)
    csvfile.close()


def savesize(result, ope, title, jobid, program_name):
    dic = dict()
    for i in range(7, 20):
        dic[2**i] = 0

    for i in range(len(result)):
        for j in range(7, 20):
            if 2**(j - 1) < result[i][0] <= 2**j:
                dic[(2**j)] += result[i][1]
                break
            elif result[i][0] <= 128:
                dic[128] += result[i][1]

    if ope == 'READ':
        co = 'r'
    else:
        if ope == 'WRITE':
            co = 'b'
    dica = sorted(dic.iteritems(), key=lambda d: d[1], reverse=True)
    dd = dict()
    if co == 'r':
        csvfile = file(
            '../../results_job_data/collect_data/' + title + '/SIZE_r.csv',
            'ab')
        writer = csv.writer(csvfile)
    else:
        if co == 'b':
            csvfile = file(
                '../../results_job_data/collect_data/' + title + '/SIZE_w.csv',
                'ab')
            writer = csv.writer(csvfile)
    for i in range(len(dica)):
        if i < 10:
            dd[dica[i][0]] = dica[i][1]
        else:
            break

    writer.writerow(['program_name and jobID ', str(program_name), str(jobid)])
    for i, key in enumerate(dd):
        writer.writerow([key / 1048576.0, dd[key], key * dd[key] / 1048576.0])

    csvfile.close()


def saveprocess(dic, pa, title, min_time, max_time, jobid, program_name,
                corehour):
    host = dict()
    con = dict()
    count = 0
    for i in range(len(dic)):
        if not host.has_key((dic[i][0], dic[i][1])):
            host[(dic[i][0], dic[i][1])] = dic[i][2] / 1024.0
        else:
            host[(
                dic[i][0],
                dic[i][1])] = host[(dic[i][0], dic[i][1])] + dic[i][2] / 1024.0

    re = [0.0 for i in range(max_time - min_time + 5)]
    for key, value in host.items():
        if value > 50:
            re[key[1]] += 1

    if pa == 'r':
        csvfile = file(
            '../../results_job_data/collect_data/' + title + '/PER.csv', 'ab')
        writer = csv.writer(csvfile)
        writer.writerow([
            'program_name and jobID ',
            str(program_name),
            str(jobid),
            str(corehour),
            str(min_time)
        ])
        for val in xrange(len(re)):
            if abs(val) > sys.float_info.epsilon:
                writer.writerow([val, re[val]])
            else:
                continue

        csvfile.close()
    else:
        if pa == 'b':
            csvfile = file(
                '../../results_job_data/collect_data/' + title + '/PEW.csv',
                'ab')
            writer = csv.writer(csvfile)
            writer.writerow([
                'program_name and jobID ',
                str(program_name),
                str(jobid),
                str(corehour),
                str(min_time)
            ])
            for val in xrange(len(re)):
                if abs(val) > sys.float_info.epsilon:
                    writer.writerow([val, re[val]])
                else:
                    continue

            csvfile.close()


def compute_pre(starttime, endtime, jobid):
    time11 = str(starttime)
    time12 = str(endtime)
    t11 = datetime.datetime.strptime(time11, '%Y-%m-%d %H:%M:%S')
    t12 = datetime.datetime.strptime(time12, '%Y-%m-%d %H:%M:%S')
    UTC = datetime.timedelta(hours=8)
    resu = []
    resu = get_re_jobid(jobid)
    print_tag = 1
    for val in resu:
        ti = val[0] + ' ' + val[1] + ' ' + val[2]
        time21 = val[3]
        time22 = val[4]
        if time22 == 'None':
            time22 = time12
        node = val[8]
        time21 = time11
        time22 = time12
        t21 = datetime.datetime.strptime(time21, '%Y-%m-%d %H:%M:%S')
        t22 = datetime.datetime.strptime(time22, '%Y-%m-%d %H:%M:%S')
        if time21 <= time11:
            time1 = time11
            t1 = t11
        else:
            time1 = time21
            t1 = t21
        if time22 >= time12:
            time2 = time12
            t2 = t12
        else:
            time2 = time22
            t2 = t22
        min_time = time_to_sec_fast(time1)
        max_time = time_to_sec_fast(time2)
        tt1 = str(t1 - UTC)
        tt2 = str(t2 - UTC)
        time1 = tt1[:10] + 'T' + tt1[11:] + '.000Z'
        time2 = tt2[:10] + 'T' + tt2[11:] + '.000Z'
        iplist = []

    for no in node:
        a = no.split('-')
        try:
            int(a[0])
        except Exception:
            print a[0]
            print 'null node!!!'
            return

        if len(a) > 1:
            for x in range(int(a[0]), int(a[1]) + 1):
                w2 = x // 1024
                w3 = (x - w2 * 1024) // 8
                w4 = x - w2 * 1024 - w3 * 8 + 1
                ip = '172.' + str(w2) + '.' + str(w3) + '.' + str(w4)
                iplist.append(ip)

        elif len(a) == 1:
            w2 = int(a[0]) // 1024
            w3 = (int(a[0]) - w2 * 1024) // 8
            w4 = int(a[0]) - w2 * 1024 - w3 * 8 + 1
            ip = '172.' + str(w2) + '.' + str(w3) + '.' + str(w4)
            iplist.append(ip)

    return (time1, time2, iplist, min_time, max_time)


def save_main(starttime, endtime, jobid, program_name, corehour, title,
              title_IOmode, host_t):
    global jobid_print
    jobid_print = jobid
    try:
        time1, time2, iplist, min_time, max_time = compute_pre(
            starttime, endtime, jobid)
    except Exception as e:
        print e

    results_message = []
    results_host = []
    count_ip = len(iplist) / node_count
    remainder = len(iplist) % node_count
    if time1[8:10] == time2[8:10]:
        index = [time1[0:4] + '.' + time1[5:7] + '.' + time1[8:10]]
    else:
        index = compute_index(time1, time2)
    for lnd in xrange(len(index)):
        if count_ip > 0:
            for c1 in xrange(count_ip):
                results_message_tmp, results_host_tmp = es_search.search(
                    time1, time2,
                    iplist[c1 * node_count:c1 * node_count + node_count],
                    index[lnd], host_t)
                results_message += results_message_tmp
                results_host += results_host_tmp

            if remainder > 0:
                results_message_tmp, results_host_tmp = es_search.search(
                    time1, time2,
                    iplist[count_ip * node_count:count_ip * node_count +
                           remainder], index[lnd], host_t)
        else:
            results_message_tmp, results_host_tmp = es_search.search(
                time1, time2, iplist, index[lnd], host_t)

    results_message += results_message_tmp
    results_host += results_host_tmp
    try:
        resultr_band, resultw_band, resultr_iops, resultw_iops, resultr_open, resultw_close, resultr_size, resultw_size, dictr, dictw, file_all_count = deal_all_message(
            results_message, results_host, min_time, max_time)
        del results_message
        del results_host
        gc.collect()
    except Exception as e:
        print e

    saveIOBANDWIDTH(resultr_band, resultw_band, title_IOmode, jobid,
                    program_name, corehour, min_time)
    saveMDS(resultr_open, resultw_close, title_IOmode, jobid, program_name,
            corehour, min_time)
    saveprocess(dictr, 'r', title_IOmode, min_time, max_time, jobid,
                program_name, corehour)
    saveprocess(dictw, 'b', title_IOmode, min_time, max_time, jobid,
                program_name, corehour)
    savesize(resultr_size, 'READ', title, jobid, program_name)
    savesize(resultw_size, 'WRITE', title, jobid, program_name)
    max_PE_r = sum_process(dictr, 'r', min_time, max_time)
    max_PE_w = sum_process(dictw, 'b', min_time, max_time)
    sum_resultr, sum_resultw, average_resultr, average_resultw, count_resultr, count_resultw, count_resultrw, average_resultr, average_resultw = sum_IOBANDWIDTH(
        resultr_band, resultw_band)
    sum_IOPS_r, sum_IOPS_w, count_IOPS_r, count_IOPS_w, count_IOPS_rw, count_IOPS_rw_all, average_IOPS_r, average_IOPS_w = sum_IOPS(
        resultr_iops, resultw_iops, resultr_band, resultw_band)
    sum_MDS_o, sum_MDS_c, count_MDS_o, count_MDS_c, count_MDS_oc, average_MDS_o, average_MDS_c = sum_MDS(
        resultr_open, resultw_close)
    return (sum_resultr, sum_resultw, count_resultr, count_resultw,
            count_resultrw, average_resultr, average_resultw, sum_IOPS_r,
            sum_IOPS_w, count_IOPS_r, count_IOPS_w, count_IOPS_rw,
            count_IOPS_rw_all, average_IOPS_r, average_IOPS_w, sum_MDS_o,
            sum_MDS_c, count_MDS_o, count_MDS_c, count_MDS_oc, average_MDS_o,
            average_MDS_c, max_PE_r, max_PE_w, file_all_count)


# okay decompiling savejob_jobid_modified.pyc
