import sys
from time_to_sec import time_to_sec, time_to_sec_fast
import csv
import exceptions
import es_search
import threading 
import datetime
import re
import numpy as np

MB_count = 1024*1024.0

def deal_host(host):
    w = host.split('.')
    cmp_node = int(w[1]) * 1024 + int(w[2]) * 8 + int(w[3])
    fwd = cmp_node//1024

    return fwd

def deal_single_message(results_message):
    resultr = 0.0
    resultw = 0.0
    result_open = 0
    result_close = 0
    resultr_ops = 0
    resultw_ops = 0
    
    resultr_size=[0.0, 0.0]
    resultw_size=[0.0, 0.0]
    dictr=[0.0, 0.0]
    dictw=[0.0, 0.0]
    file_name = 'NULL'
    hash_file_name = 0
    
    try:
        x = (results_message).split()
        time = x[0]+" "+x[1]
    #    c_time = time[1:-1]
        ke = x[6]
        kee = x[3]
        
        if "OPEN" in  ke:
            result_open = 1
            file_name = x[7]
#            hash_file_name = hash(file_name)
#            print file_name
#            print hash_file_name
        elif "RELEASE" in ke:
            result_close = 1
        elif("offset" not in results_message):
            try:
                size = x[4].split("=")[1]
                op_count = int(x[5].split("=")[1])
                sumsize = int(size)
                if("READ" in kee):
                    resultr = sumsize / MB_count
                    resultr_ops = op_count
                    resultr_size = [sumsize/op_count*1.0,op_count]
                    dictr = [sumsize, op_count]
                elif("WRITE" in kee):
                    resultw = sumsize / MB_count
                    resultw_ops = op_count
                    resultw_size = [sumsize/op_count*1.0,op_count]
                    dictw = [sumsize, op_count]
            except Exception as e:
#                print ke
                print x
                print e
        else:
            try:
                size = int(x[5].split("=")[1])
                op_count = int(x[7].split("=")[1])
                sumsize = int(size)*op_count
                if("READ" in kee):
                    resultr = 1.0*sumsize / MB_count
                    resultr_ops = op_count
                    resultr_size = [size, op_count]
                    dictr = [sumsize, op_count]
                elif("WRITE" in kee):
                    resultw = 1.0*sumsize / MB_count
                    resultw_ops = op_count
                    resultw_size = [size, op_count]
                    dictw = [sumsize, op_count]
            except Exception as e:
#                print ke
                print x
                print e

    except Exception as e:
        print e 
        print x 

    return time, resultr, resultw, resultr_ops, resultw_ops, \
    result_open, result_close, resultr_size, resultw_size, dictr, dictw, file_name

def deal_single_message_fd(results_message):
    resultr = 0.0
    resultw = 0.0
    result_open = 0
    result_close = 0
    resultr_ops = 0
    resultw_ops = 0
    
    resultr_size=[0.0, 0.0]
    resultw_size=[0.0, 0.0]
    dictr=[0.0, 0.0]
    dictw=[0.0, 0.0]
    file_name = 'NULL'
    fd = 'NULL'

    try:
        x = (results_message).split()
        time = x[0]+" "+x[1]
    #    c_time = time[1:-1]
        ke = x[6]
        kee = x[3]
        
        if "OPEN" in  ke:
            result_open = 1
            file_name = x[7]
            try:
                fd = x[9]
            except Exception as e:
#                print x
#                print e
                 nofd=1
        elif "RELEASE" in ke:
            result_close = 1
        elif("offset" not in results_message):
            try:
                size = x[4].split("=")[1]
                op_count = int(x[5].split("=")[1])
                sumsize = int(size)
                if("READ" in kee):
                    resultr = sumsize / MB_count
                    resultr_ops = op_count
                    resultr_size = [sumsize/op_count*1.0,op_count]
                    dictr = [sumsize, op_count]
                elif("WRITE" in kee):
                    resultw = sumsize / MB_count
                    resultw_ops = op_count
                    resultw_size = [sumsize/op_count*1.0,op_count]
                    dictw = [sumsize, op_count]
            except Exception as e:
#                print ke
                print x
                print e
        else:
            try:
                size = int(x[5].split("=")[1])
                op_count = int(x[7].split("=")[1])
                sumsize = int(size)*op_count
                if("READ" in kee):
                    resultr = 1.0* sumsize / MB_count
                    resultr_ops = op_count
                    resultr_size = [size, op_count]
                    dictr = [sumsize, op_count]
                    fd = x[4]
                elif("WRITE" in kee):
                    resultw = 1.0* sumsize / MB_count
                    resultw_ops = op_count
                    resultw_size = [size, op_count]
                    dictw = [sumsize, op_count]
                    fd = x[4]
            except Exception as e:
#                print ke
                print x
                print e

    except Exception as e:
        print e 
        print x 

    return time, resultr, resultw, resultr_ops, resultw_ops, \
    result_open, result_close, resultr_size, resultw_size, dictr, dictw, \
    file_name, fd


def deal_all_message(results_message, results_host, min_time, max_time):

    resultr = np.array([0.0 for i in range(max_time-min_time+5)])
    resultw = np.array([0.0 for i in range(max_time-min_time+5)])
    result_open = np.array([0 for i in range(max_time-min_time+5)])
    result_close = np.array([0 for i in range(max_time-min_time+5)])
    resultr_ops = np.array([0 for i in range(max_time-min_time+5)])
    resultw_ops = np.array([0 for i in range(max_time-min_time+5)])
    resultr_size = []
    resultw_size = []
    dictr = []
    dictw = []
     
    file_open = [set() for i in range(max_time-min_time+5)]
    file_all_set = set()
    fd_set = set()
    fd_info = dict()
    fwd_file_map = dict()

    #fd_info[fd] = {{file_name: file_name}; {time:{time_second: {read: }{write: }}}} 
    for i in xrange(len(results_message)):
        try:
            time, resultr_tmp, resultw_tmp, resultr_ops_tmp, resultw_ops_tmp, \
            result_open_tmp, result_close_tmp, resultr_size_tmp, \
            resultw_size_tmp, dictr_tmp, dictw_tmp, file_name, fd\
            = deal_single_message_fd(results_message[i])
        except Exception as e:
            print e
#            print results_message[i]
        
        try:
            if(fd != 'NULL'):
                fd_set.add(fd)
                if(fd in fd_info):
                    if(file_name != 'NULL'):
                        fd_info[fd]['file_name'] = file_name
                    if(time in fd_info[fd]['time']):
                        fd_info[fd]['time'][time]['read'] += resultr_tmp
                        fd_info[fd]['time'][time]['write'] += resultw_tmp
                    else:
                        fd_info[fd]['time'][time] = {}
                        fd_info[fd]['time'][time]['read'] = 0
                        fd_info[fd]['time'][time]['write'] = 0
                else:
                    fd_info[fd] = {}
                    fd_info[fd]['time'] = {}
                    fd_info[fd]['file_name'] = ''
            index = int(time_to_sec(time[1:-1])) - min_time +1
#            print index
            result_open[index] += result_open_tmp
            result_close[index] += result_close_tmp
            resultr[index] += resultr_tmp
            resultw[index] += resultw_tmp
            resultr_ops[index] += resultr_ops_tmp
            resultw_ops[index] += resultw_ops_tmp
            if(file_name != 0):
                file_open[index].add(file_name)
                file_all_set.add(file_name)
#            if(abs(resultr_size_tmp[0]) > sys.float_info.epsilon and \
#               abs(resultr_size_tmp[1]) > sys.float_info.epsilon):
            resultr_size.append(resultr_size_tmp)
#            if(abs(resultw_size_tmp[0]) > sys.float_info.epsilon and \
#               abs(resultw_size_tmp[1]) > sys.float_info.epsilon):
            resultw_size.append(resultw_size_tmp)
#            if(abs(dictr_tmp[0]) > sys.float_info.epsilon and \
#               abs(dictr_tmp[1]) > sys.float_info.epsilon):
            dictr.append([results_host[i], index, dictr_tmp[0], dictr_tmp[1]])
#            if(abs(dictw_tmp[0]) > sys.float_info.epsilon and \
#               abs(dictw_tmp[1]) > sys.float_info.epsilon):
            dictw.append([results_host[i], index, dictw_tmp[0], dictw_tmp[1]])
            fwd = deal_host(results_host[i])
            if(fwd in fwd_file_map):
                fwd_file_map[fwd].add(file_name)
            else:
                fwd_file_map[fwd] = set([file_name])

        except Exception as e:
            #print e
            continue
#    print file_set_open[0]
#    for i in xrange(len(file_set_open)):
#        file_all_set |= file_set_open[i]
#    print file_all_set
#    print len(file_all_set)
    for fd in fd_info:
        fd_info[fd]['total_time'] = len(fd_info[fd]['time'])
        fd_info[fd]['sum_read_size'] = 0
        fd_info[fd]['sum_write_size'] = 0
        time_seq = []
        for time in fd_info[fd]['time']:
            time_seq.append([time])
            fd_info[fd]['sum_read_size'] += \
            fd_info[fd]['time'][time]['read']
            fd_info[fd]['sum_write_size'] += \
            fd_info[fd]['time'][time]['write']
        try:
            fd_info[fd]['start_time'] = min(time_seq)
            fd_info[fd]['end_time'] = max(time_seq)
        except Exception as e:
            fd_info[fd]['start_time'] = '[0000-00-00 00:00:00]'
            fd_info[fd]['end_time'] = '[0000-00-00 00:00:00]'
            

    file_all_count = len(file_all_set)
    return resultr, resultw, resultr_ops, resultw_ops, result_open, result_close, \
    resultr_size, resultw_size, dictr, dictw, file_all_count, file_open, fd_info, \
    fwd_file_map

def deal_part_message(resultr, resultw, result_open, result_close, \
resltr_ops,resultw_ops, resultr_size, resultw_size, dictr, dictw, \
results_message, file_open, file_all_set, \
results_host, min_time, max_time):
    
    for i in xrange(len(results_message)):
        try:
            time, resultr_tmp, resultw_tmp, resultr_ops_tmp, resultw_ops_tmp, \
            result_open_tmp, result_close_tmp, resultr_size_tmp, resultw_size_tmp, \
            dictr_tmp, dictw_tmp, file_name\
            = deal_single_message(results_message[i])
        except Exception as e:
            print e
#            print results_message[i]
        
        try:
            index = int(time_to_sec(time[1:-1])) - min_time +1
            result_open[index] += result_open_tmp
            result_close[index] += result_close_tmp
            resultr[index] += resultr_tmp
            resultw[index] += resultw_tmp
            resultr_ops[index] += resultr_ops_tmp
            resultw_ops[index] += resultw_ops_tmp
            if(file_name != 0):
                file_open[index].add(file_name)
                file_all_set.add(file_name)
#            if(abs(resultr_size_tmp[0]) > sys.float_info.epsilon and \
#               abs(resultr_size_tmp[1]) > sys.float_info.epsilon):
            resultr_size.append(resultr_size_tmp)
#            if(abs(resultw_size_tmp[0]) > sys.float_info.epsilon and \
#               abs(resultw_size_tmp[1]) > sys.float_info.epsilon):
            resultw_size.append(resultw_size_tmp)
#            if(abs(dictr_tmp[0]) > sys.float_info.epsilon and \
#               abs(dictr_tmp[1]) > sys.float_info.epsilon):
            dictr.append([results_host[i], index, dictr_tmp[0], dictr_tmp[1]])
#            if(abs(dictw_tmp[0]) > sys.float_info.epsilon and \
#               abs(dictw_tmp[1]) > sys.float_info.epsilon):
            dictw.append([results_host[i], index, dictw_tmp[0], dictw_tmp[1]])
        except Exception as e:
            print e
            continue
#    print file_set_open[0]
#    for i in xrange(len(file_set_open)):
#        file_all_set |= file_set_open[i]
#    print file_all_set
#    print len(file_all_set)
def ost_deal_message(ost_message, ost_time, start_time, end_time):
    ostlist=[]
    result = []
    for i in range(len(ost_message)):
        result.append(ost_message[i] + ' ' + ost_time[i])
    result.sort()

    length = time_to_sec_fast(end_time) - time_to_sec_fast(start_time)
    #print length
    bandr=[([0]*(length+5)) for i in range(440)]
    bandw=[([0]*(length+5)) for i in range(440)]
    t1=datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
    print "Reshape and sort done..."
    lg=len(result)
    if lg<1:
        return ostlist,bandr,bandw
    x = result[0].split(' ')
    ost_p=x[0]
    read_p = 0
    write_p = 0
    for i in range(len(x)/3):
        size = re.sub("\D", "", x[1+3*i])
        read_count = re.sub("\D", "", x[2+3*i])
        write_count = re.sub("\D", "", x[3+3*i])
        read_p += int(size)*int(read_count)
        write_p += int(size)*int(write_count)

    time_p=str(x[28])[:10]+" "+str(x[28])[11:-5]
    t2=datetime.datetime.strptime(time_p,'%Y-%m-%d %H:%M:%S')
    time_interval=str(t2-t1).split(':')
    t_p=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
    print "Deal data..."
    read_count=0
    write_count=0
    for item in range(1,lg):
        try:
            y=result[item].split(' ')
            ost=y[0]

            read = 0
            write = 0
            for i in range(len(x)/3):
                size = re.sub("\D", "", y[1+3*i])
                read_count = re.sub("\D", "", y[2+3*i])
                write_count = re.sub("\D", "", y[3+3*i])
                read += int(size)*int(read_count)
                write += int(size)*int(write_count)

            time=str(y[28])[:10]+" "+str(y[28])[11:-5]
            t3=datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
            time_interval=str(t3-t1).split(':')
            t=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
            if ost==ost_p:
                interval=t-t_p
                #print interval," ",t_p," ",band_number
                OST_number=int('0x'+ost,16)
                read_value=int(read)-int(read_p)
                write_value=int(write)-int(write_p)
                if interval>0 and interval<1000:
                    for j in range(interval):
                        bandr[OST_number][t_p+j]+=read_value/1024.0*4/interval
                        bandw[OST_number][t_p+j]+=write_value/1024.0*4/interval
                ost_p=ost
                read_p=read
                write_p=write
                t_p=t
                if OST_number not in ostlist:
                    ostlist.append(OST_number)
            else:
                x=result[item].split(' ')
                ost_p=x[0]

                read_p = 0
                write_p = 0
                for i in range(len(x)/3):
                    size = re.sub("\D", "", x[1+3*i])
                    read_count = re.sub("\D", "", x[2+3*i])
                    write_count = re.sub("\D", "", x[3+3*i])
                    read_p += int(size)*int(read_count)
                    write_p += int(size)*int(write_count)
                
                time_p=str(x[28])[:10]+" "+str(x[28])[11:-5]
                t2=datetime.datetime.strptime(time_p,'%Y-%m-%d %H:%M:%S')
                time_interval=str(t2-t1).split(':')
                t_p=int(time_interval[0])*3600+int(time_interval[1])*60+int(time_interval[2])
        except Exception as e:
            print e," size: ",size," read_count: ",read_count," write_count: ",write_count," time_interval: ",time_interval
            print y
            continue

    return ostlist,bandr,bandw

def fwd_deal_message(ost_message, ost_time, start_time, end_time):

    length = time_to_sec_fast(end_time) - time_to_sec_fast(start_time)
    #print length
    fwd_bandr = [0 for i in range(length)]
    fwd_bandw = [0 for i in range(length)]

    ostlist, bandr, bandw = ost_deal_message(ost_message, ost_time, start_time, end_time)
    for j in range(length):
        for i in range(440):
            fwd_bandr[j] += bandr[i][j]        
            fwd_bandw[j] += bandw[i][j]

    return ostlist, fwd_bandr, fwd_bandw

