#!/usr/bin/python
import csv
import sys
import datetime

all_file_name = '/home/export/mount_test/swstorage/source_job_data/JOB_log_all.csv'
other_file_name = '/home/export/mount_test/swstorage/source_job_data/JOB_log_other.csv'
file_name = '/home/export/mount_test/swstorage/source_job_data/JOB_log.csv'


def read_big_job():

    jobID = []
    start_time = []
    end_time = []
    CNC = []
    run_time = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) >= 4):
                if (line[4].strip()):
                    compute_node_count_tmp = int(line[4].strip())
                if (line[10].strip()):
                    run_time_tmp = int(line[10].strip())
                if (run_time_tmp > 5 * 86400
                        or compute_node_count_tmp > 15000):
                    jobID.append(line[0].strip())
                    start_time.append(line[8].strip())
                    end_time.append(line[9].strip())
                    CNC.append(int(line[4].strip()))
                    run_time.append(int(line[10].strip()))

    return jobID, start_time, end_time, CNC, run_time


def select_jobid_month(month):

    jobID = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) == month):
                if (line[4].strip()):
                    jobID.append(line[0].strip())

    return jobID


def read_jobID_prog_month(month):

    jobID = []
    prog_name = []
    CNC = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) == month):
                jobID.append(line[0].strip())
                prog_name.append(line[14].strip())
                CNC.append(line[4].strip())

    return jobID, prog_name, CNC


def read_job_core():

    job_core = dict()

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            job_core[line[0].strip()] = {}
            job_core[int(line[0].strip())]['core'] = int(line[5])

    return job_core


def read_runtime():

    jobID = []
    run_time = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) >= 4):
                if (line[0].strip()):
                    jobID.append(line[0].strip())
                if (line[10].strip()):
                    run_time.append(float(line[10].strip()))

    return jobID, run_time


def read_CNC():

    jobID = []
    compute_node_count = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) >= 4):
                if (line[0].strip()):
                    jobID.append(line[0].strip())
                if (line[4].strip()):
                    compute_node_count.append(int(line[4].strip()))

    return jobID, compute_node_count


def read_CNC_runtime_corehour():

    jobID = []
    compute_node_count = []
    run_time = []
    corehour = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) >= 4):
                if (line[0].strip()):
                    jobID.append(line[0].strip())
                if (line[4].strip()):
                    compute_node_count.append(int(line[4].strip()))
                if (line[10].strip()):
                    run_time.append(float(line[10].strip()))
                if (line[10].strip()):
                    corehour.append(float(line[6].strip()))

    return jobID, compute_node_count, run_time, corehour


def read_corehour():

    corehour = dict()

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            if(int((line[7].split('-'))[0]) >= 2017 and \
            int((line[7].split('-'))[1]) >= 4):
                corehour[line[0].strip()] = float(line[6].strip())

    return corehour


def read_CNlist():

    jobID = []
    start_time = []
    end_time = []
    CNlist = []

    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            jobID.append(line[0].strip())
            start_time.append(line[8].strip())
            end_time.append(line[9].strip())
            CNlist.append(line[15].strip())
            if (len(line[15].strip()) >= 20000):
                print line[15].strip()

    return jobID, start_time, end_time, CNlist


def read_wait_time():

    jobID = []
    wait_time = []
    total_seconds = 0
    count = 0
    reader = csv.reader(open(file_name, 'rU'), dialect=csv.excel_tab)
    for line in reader:
        if (len(line) >= 16):
            jobID.append(line[0].strip())
            submit_time = line[7].strip()
            start_time = line[8].strip()

            submit_time_format = datetime.datetime.strptime(
                submit_time, '%Y-%m-%d %H:%M:%S')
            start_time_format = datetime.datetime.strptime(
                start_time, '%Y-%m-%d %H:%M:%S')
            delta = start_time_format - submit_time_format
            total_seconds += delta.total_seconds()
            count += 1

    ave_wait_time = total_seconds / count
    print "Average wait time: ", ave_wait_time

    return jobID, wait_time


if __name__ == "__main__":

    jobID, wait_time = read_wait_time()
#    jobID, start_time, end_time, CNlist = read_CNlist()
