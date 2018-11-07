import csv
from read_from_source import read_job_core
from read_IOmode_DB_volume import get_job_bene_info, get_corehour_jobnum

job_info_name = '/home/export/mount_test/swstorage/source_job_data/JOB_log.csv'
IOBW_file_name = '/home/export/mount_test/swstorage/results_job_data/collect_data/all_data/IOBW.csv'
IOPS_file_name = '/home/export/mount_test/swstorage/results_job_data/collect_data/all_data/IOPS.csv'
MDS_file_name = '/home/export/mount_test/swstorage/results_job_data/collect_data/all_data/MDS.csv'
maxPE_file_name = '/home/export/mount_test/swstorage/results_job_data/collect_data/all_data/maxPE2.csv'

source_file_name = '/home/export/mount_test/swstorage/source_job_data/JOB_log.csv'

IO_mode_file_r = '/home/export/mount_test/swstorage/results_job_data/result_data/IOmode_by_volumn/IO_mode_r_count.csv'
IO_mode_file_w = '/home/export/mount_test/swstorage/results_job_data/result_data/IOmode_by_volumn/IO_mode_w_count.csv'

threshold1 = 0.5
threshold2 = 0.33

interval1 = 32
interval2 = 256
interval3 = 1000
interval4 = 8000

corehour_interval0 = 0
corehour_interval1 = 10
corehour_interval2 = 100
corehour_interval3 = 1000
corehour_interval4 = 10000
corehour_interval5 = 100000

high_mds = 1000
high_volume = 20000.0
total_job_num, total_corehour = get_corehour_jobnum()

#IO_mode dict() : IO_mode[jobid] = { 'mds': ;'avg_mds' = ;'io_volume': ;'pe_r': ;'pe_w': ;'mode': ;
#'core': ;}

#Read all info needed.


def aggregate_R_W(IO_mode_r, IO_mode_w):
    for job in IO_mode_r:
        if (IO_mode_w.has_key(job)):
            tmp_IOmode_r = IO_mode_r[job]['mode']
            tmp_IOmode_w = IO_mode_w[job]['mode']
            if (tmp_IOmode_r == 'NtoN' or tmp_IOmode_w == 'NtoN'):
                IO_mode_r[job]['mode'] = 'NtoN'
            elif (tmp_IOmode_r == 'Nto1' or tmp_IOmode_w == 'Nto1'):
                IO_mode_r[job]['mode'] = 'Nto1'
            elif (tmp_IOmode_r == '1to1' or tmp_IOmode_w == '1to1'):
                IO_mode_r[job]['mode'] = '1to1'

    for job in IO_mode_w:
        if (not IO_mode_r.has_key(job)):
            IO_mode_r[job] = {}
            IO_mode_r[job]['mode'] = IO_mode_w[job]['mode']
            #            IO_mode_r[job]['mds'] = IO_mode_w[job]['mds']
            IO_mode_r[job]['avg_mds'] = IO_mode_w[job]['avg_mds']
            IO_mode_r[job]['io_volume'] = IO_mode_w[job]['io_volume']
            IO_mode_r[job]['pe_r'] = IO_mode_w[job]['pe_r']
            IO_mode_r[job]['pe_w'] = IO_mode_w[job]['pe_w']
            IO_mode_r[job]['mode'] = IO_mode_w[job]['mode']
            IO_mode_r[job]['corehour'] = IO_mode_w[job]['corehour']


#            IO_mode_r[job]['core'] = IO_mode_w[job]['core']


def judge_benefit_job(IO_mode):

    job_benefit = set()
    job_volume_less = set()
    job_pe_less32 = set()
    job_mds_more1k = set()
    job_all_set = set()

    for job in IO_mode:
        job_all_set.add(job)
        try:
            if((IO_mode[job]['mode'] == 'NtoN' or IO_mode[job]['mode'] == 'Nto1') and \
            IO_mode[job]['io_volume'] >= high_volume and \
            IO_mode[job]['avg_mds'] <= high_mds and \
            (IO_mode[job]['pe_r'] >= 32 or IO_mode[job]['pe_w'] >= 32)):
                job_benefit.add(job)
            elif((IO_mode[job]['pe_r'] < 32 and IO_mode[job]['pe_w'] < 32) or \
            IO_mode[job]['mode'] == '1to1'):
                job_pe_less32.add(job)
            elif(IO_mode[job]['avg_mds'] > high_mds and \
            IO_mode[job]['io_volume'] >= high_volume):
                job_mds_more1k.add(job)
            else:
                job_volume_less.add(job)
        except Exception as e:
            print e
            continue

    print len(set(IO_mode.keys()))
    job_unknow = set(IO_mode.keys()) - job_benefit - job_volume_less - \
    job_pe_less32 - job_mds_more1k

    ch_bene = 0
    ch_32 = 0
    ch_mds = 0
    ch_volume = 0

    for job in job_benefit:
        ch_bene += IO_mode[job]['corehour']

    for job in job_pe_less32:
        ch_32 += IO_mode[job]['corehour']

    for job in job_mds_more1k:
        ch_mds += IO_mode[job]['corehour']

    for job in job_volume_less:
        ch_volume += IO_mode[job]['corehour']

    print "%d %f" % (len(job_benefit), ch_bene)
    print "%d %f" % (len(job_pe_less32), ch_32)
    print "%d %f" % (len(job_mds_more1k), ch_mds)
    print "%d %f" % (len(job_volume_less), ch_volume)

    print "Total number of job: %d .\n" % (len(IO_mode))

    print "Job number of benefit: %d percentage: %f corehour: %f percentage: %f.\n"\
    %((len(job_benefit)), (float((len(job_benefit))/total_job_num)), \
    ch_bene, ch_bene/ total_corehour)

    print "Job number of process-num less than 32 : %d percentage: %f corehour: %f percentage: %f.\n"\
    %(len(job_pe_less32), len(job_pe_less32)/total_job_num, ch_32, ch_32/ total_corehour)

    print "Job number of IO_volume less than %d MB : %d percentage: %f corehour: %f percentage: %f.\n"\
    %(high_volume, len(job_volume_less), len(job_volume_less)/total_job_num, \
    ch_volume, ch_volume/ total_corehour)

    print "Job number of mds more than 1K : %d percentage: %f corehour: %f percentage: %f.\n"%(len(job_mds_more1k), \
    len(job_mds_more1k)/total_job_num, ch_mds, ch_mds/ total_corehour)


def group(IO_mode):
    NtoN_32 = 0
    NtoN_256 = 0
    NtoN_1k = 0
    NtoN_8k = 0

    Nto1_32 = 0
    Nto1_256 = 0
    Nto1_1k = 0
    Nto1_8k = 0

    oneto1_32 = 0
    oneto1_256 = 0
    oneto1_1k = 0
    oneto1_8k = 0

    for job in IO_mode:
        if (IO_mode[job]['mode'] == 'NtoN'):
            if(IO_mode[job]['CNC'] >= interval1 and  \
            IO_mode[job]['CNC'] < interval2):
                NtoN_32 += 1
            elif(IO_mode[job]['CNC'] >= interval2 and  \
            IO_mode[job]['CNC'] < interval3):
                NtoN_256 += 1
            elif(IO_mode[job]['CNC'] >= interval3 and  \
            IO_mode[job]['CNC'] < interval4):
                NtoN_1k += 1
            elif (IO_mode[job]['CNC'] >= interval4):
                NtoN_8k += 1
        elif (IO_mode[job]['mode'] == 'Nto1'):
            if(IO_mode[job]['CNC'] >= interval1 and  \
            IO_mode[job]['CNC'] < interval2):
                Nto1_32 += 1
            elif(IO_mode[job]['CNC'] >= interval2 and  \
            IO_mode[job]['CNC'] < interval3):
                Nto1_256 += 1
            elif(IO_mode[job]['CNC'] >= interval3 and  \
            IO_mode[job]['CNC'] < interval4):
                Nto1_1k += 1
            elif (IO_mode[job]['CNC'] >= interval4):
                Nto1_8k += 1
        elif (IO_mode[job]['mode'] == '1to1'):
            if(IO_mode[job]['CNC'] >= interval1 and  \
            IO_mode[job]['CNC'] < interval2):
                oneto1_32 += 1
            elif(IO_mode[job]['CNC'] >= interval2 and  \
            IO_mode[job]['CNC'] < interval3):
                oneto1_256 += 1
            elif(IO_mode[job]['CNC'] >= interval3 and  \
            IO_mode[job]['CNC'] < interval4):
                oneto1_1k += 1
            elif (IO_mode[job]['CNC'] >= interval4):
                print job
                oneto1_8k += 1

    print "NtoN: range[32, 256): %d." % (NtoN_32)
    print "NtoN: range[256, 1k): %d." % (NtoN_256)
    print "NtoN: range[1k, 8k): %d." % (NtoN_1k)
    print "NtoN: range[8k, inf): %d." % (NtoN_8k)

    print "Nto1: range[32, 256): %d." % (Nto1_32)
    print "Nto1: range[256, 1k): %d." % (Nto1_256)
    print "Nto1: range[1k, 8k): %d." % (Nto1_1k)
    print "Nto1: range[8k, inf): %d." % (Nto1_8k)

    print "1to1: range[32, 256): %d." % (oneto1_32)
    print "1to1: range[256, 1k): %d." % (oneto1_256)
    print "1to1: range[1k, 8k): %d." % (oneto1_1k)
    print "1to1: range[8k, inf): %d." % (oneto1_8k)


def print_NtoM_read():
    print "NtoM: range[32, 256): 23."
    print "NtoM: range[256, 1k): 68."
    print "NtoM: range[1k, 8k): 104."
    print "NtoM: range[8k, inf): 5."


def print_NtoM_write():
    print "NtoM: range[32, 256): 29."
    print "NtoM: range[256, 1k): 45."
    print "NtoM: range[1k, 8k): 77."
    print "NtoM: range[8k, inf): 4."


def group_corehour(IO_mode):
    NtoN_0 = 0
    NtoN_1 = 0
    NtoN_2 = 0
    NtoN_3 = 0
    NtoN_4 = 0
    NtoN_5 = 0

    Nto1_0 = 0
    Nto1_1 = 0
    Nto1_2 = 0
    Nto1_3 = 0
    Nto1_4 = 0
    Nto1_5 = 0

    oneto1_0 = 0
    oneto1_1 = 0
    oneto1_2 = 0
    oneto1_3 = 0
    oneto1_4 = 0
    oneto1_5 = 0

    for job in IO_mode:
        if (IO_mode[job]['mode'] == 'NtoN'):
            if(IO_mode[job]['corehour'] >= corehour_interval0 and \
            IO_mode[job]['corehour'] < corehour_interval1):
                NtoN_0 += 1
            if(IO_mode[job]['corehour'] >= corehour_interval1 and \
            IO_mode[job]['corehour'] < corehour_interval2):
                NtoN_1 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval2 and \
            IO_mode[job]['corehour'] < corehour_interval3):
                NtoN_2 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval3 and \
            IO_mode[job]['corehour'] < corehour_interval4):
                NtoN_3 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval4 and \
            IO_mode[job]['corehour'] < corehour_interval5):
                NtoN_4 += 1
            elif (IO_mode[job]['corehour'] >= corehour_interval5):
                NtoN_5 += 1
        elif (IO_mode[job]['mode'] == 'Nto1'):
            if(IO_mode[job]['corehour'] >= corehour_interval0 and \
            IO_mode[job]['corehour'] < corehour_interval1):
                Nto1_0 += 1
            if(IO_mode[job]['corehour'] >= corehour_interval1 and \
            IO_mode[job]['corehour'] < corehour_interval2):
                Nto1_1 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval2 and \
            IO_mode[job]['corehour'] < corehour_interval3):
                Nto1_2 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval3 and \
            IO_mode[job]['corehour'] < corehour_interval4):
                Nto1_3 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval4 and \
            IO_mode[job]['corehour'] < corehour_interval5):
                Nto1_4 += 1
            elif (IO_mode[job]['corehour'] >= corehour_interval5):
                Nto1_5 += 1
        elif (IO_mode[job]['mode'] == '1to1'):
            if(IO_mode[job]['corehour'] >= corehour_interval0 and \
            IO_mode[job]['corehour'] < corehour_interval1):
                oneto1_0 += 1
            if(IO_mode[job]['corehour'] >= corehour_interval1 and \
            IO_mode[job]['corehour'] < corehour_interval2):
                oneto1_1 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval2 and \
            IO_mode[job]['corehour'] < corehour_interval3):
                oneto1_2 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval3 and \
            IO_mode[job]['corehour'] < corehour_interval4):
                oneto1_3 += 1
            elif(IO_mode[job]['corehour'] >= corehour_interval4 and \
            IO_mode[job]['corehour'] < corehour_interval5):
                oneto1_4 += 1
            elif (IO_mode[job]['corehour'] >= corehour_interval5):
                oneto1_5 += 1

    print "NtoN: range[0, 10): %d." % (NtoN_0)
    print "NtoN: range[10, 100): %d." % (NtoN_1)
    print "NtoN: range[100, 1000): %d." % (NtoN_2)
    print "NtoN: range[1000, 10000): %d." % (NtoN_3)
    print "NtoN: range[10000, 100000): %d." % (NtoN_4)
    print "NtoN: range[100000, inf): %d." % (NtoN_5)

    print "Nto1: range[0, 10): %d." % (Nto1_0)
    print "Nto1: range[10, 100): %d." % (Nto1_1)
    print "Nto1: range[100, 1000): %d." % (Nto1_2)
    print "Nto1: range[1000, 10000): %d." % (Nto1_3)
    print "Nto1: range[10000, 100000): %d." % (Nto1_4)
    print "Nto1: range[100000, inf): %d." % (Nto1_5)

    print "oneto1: range[0, 10): %d." % (oneto1_0)
    print "oneto1: range[10, 100): %d." % (oneto1_1)
    print "oneto1: range[100, 1000): %d." % (oneto1_2)
    print "oneto1: range[1000, 10000): %d." % (oneto1_3)
    print "oneto1: range[10000, 100000): %d." % (oneto1_4)
    print "oneto1: range[100000, inf): %d." % (oneto1_5)


def benefit_main():
    IO_mode_r = get_job_bene_info('read')
    IO_mode_w = get_job_bene_info('write')
    aggregate_R_W(IO_mode_r, IO_mode_w)
    judge_benefit_job(IO_mode_r)


def main_IOmode_corehour():
    IO_mode_r = get_job_bene_info('read')
    IO_mode_w = get_job_bene_info('write')
    print "Read result:"
    group_corehour(IO_mode_r)
    print "Write result:"
    group_corehour(IO_mode_w)


if __name__ == "__main__":

    #    benefit_main()
    main_IOmode_corehour()
