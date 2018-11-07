import MySQLdb
import MySQLdb.cursors
import sys

threshold1 = 0.5
threshold2 = 0.33

IOmode_table_read = 'JOB_IOMODE_READ'
IOmode_table_write = 'JOB_IOMODE_WRITE'
IOperf_table = 'JOB_IO_INFO'

Mysql_ip = '20.0.2.201'
Mysql_usr = 'root'
Mysql_db = 'JOB_IO'
Mysql_passwd = ''
Mysql_port = 3306


def get_corehour_jobnum():

    conn = MySQLdb.connect(
        host=Mysql_ip,
        user=Mysql_usr,
        db=Mysql_db,
        passwd=Mysql_passwd,
        port=Mysql_port)
    cursor = conn.cursor()
    sql = "select count(*), sum(corehour) from JOB_IO_INFO where IOBW_READ_SUM > 0.0 or IOBW_WRITE_SUM > 0.0;"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    return float(result[0][0]), float(result[0][1])


def read_IOmode_DB(table):
    IO_mode = dict()
    conn = MySQLdb.connect(
        host=Mysql_ip,
        user=Mysql_usr,
        db=Mysql_db,
        passwd=Mysql_passwd,
        port=Mysql_port)
    cursor = conn.cursor()
    if (table == IOmode_table_read):
        #        sql = "select * from %s where convert(jobid, unsigned) < 41000000 group by jobid having count(*) > 1;"%(table)
        sql = "select * from %s group by jobid having count(*) > 1;"\
        %(table)
    else:
        #        sql = "select * from %s where convert(jobid, unsigned) < 41000000;"%(table)
        sql = "select * from %s;" % (table)

    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    for res in result:
        if (not IO_mode.has_key(res[0])):
            IO_mode[res[0]] = {}
            IO_mode[res[0]]['CNC'] = int(res[1])
            IO_mode[res[0]]['runtime'] = int(res[2])
            IO_mode[res[0]]['corehour'] = float(res[3])
            IO_mode[res[0]]['iomode'] = {}
            IO_mode[res[0]]['iomode'][str(res[4])] \
            = float(res[5])
        else:
            if(IO_mode[res[0]]['iomode'].\
            has_key(str(res[4]))):
                IO_mode[res[0]]['iomode'][str(res[4])] \
                += float(res[5])
            else:
                IO_mode[res[0]]['iomode'][str(res[4])] \
                = float(res[5])

    return IO_mode


def cal_IOmode_by_volume_NtoN_priv(jobinfo):
    IO_mode = dict()

    for job in jobinfo:
        IO_mode[job] = {}
        total_val = 0
        for iomode in jobinfo[job]['iomode']:
            total_val += jobinfo[job]['iomode'][iomode]
            if (len(jobinfo[job]['iomode']) == 1):
                IO_mode[job]['mode'] = \
                (jobinfo[job]['iomode'].keys())[0]
            elif (len(jobinfo[job]['iomode']) == 2):
                if ('NtoN' in jobinfo[job]['iomode']):
                    IO_mode[job]['mode'] = 'NtoN'
                else:
                    for iomode in jobinfo[job]['iomode']:
                        if(jobinfo[job]['iomode'][iomode] / total_val \
                        > threshold1 ):
                            IO_mode[job]['mode'] = iomode
            elif (len(jobinfo[job]['iomode']) >= 3):
                if ('NtoN' in jobinfo[job]['iomode']):
                    IO_mode[job]['mode'] = 'NtoN'
                else:
                    for iomode in jobinfo[job]['iomode']:
                        if(jobinfo[job]['iomode'][iomode] / total_val \
                        > threshold2 ):
                            IO_mode[job]['mode'] = iomode

    return IO_mode


def cal_IOmode_by_volume(jobinfo):
    IO_mode = dict()

    for job in jobinfo:
        IO_mode[job] = {}
        total_val = 0
        for iomode in jobinfo[job]['iomode']:
            total_val += jobinfo[job]['iomode'][iomode]
            if (len(jobinfo[job]['iomode']) == 1):
                IO_mode[job]['mode'] = \
                (jobinfo[job]['iomode'].keys())[0]
            elif (len(jobinfo[job]['iomode']) == 2):
                for iomode in jobinfo[job]['iomode']:
                    if(jobinfo[job]['iomode'][iomode] / total_val \
                    > threshold1 ):
                        IO_mode[job]['mode'] = iomode
            elif (len(jobinfo[job]['iomode']) >= 3):
                for iomode in jobinfo[job]['iomode']:
                    if(jobinfo[job]['iomode'][iomode] / total_val \
                    > threshold2 ):
                        IO_mode[job]['mode'] = iomode

    return IO_mode


def get_perf_info(IO_mode, table):
    jobinfo = dict()

    conn = MySQLdb.connect(
        host=Mysql_ip,
        user=Mysql_usr,
        db=Mysql_db,
        passwd=Mysql_passwd,
        port=Mysql_port)
    cursor = conn.cursor()
    sql = "select JOBID, CNC, COREHOUR, IOBW_READ_SUM + IOBW_WRITE_SUM, \
    MDS_OPEN_SUM, PROCESS_READ_MAX, \
    PROCESS_WRITE_MAX from %s where \
    IOBW_READ_SUM > 0.0 or IOBW_WRITE_SUM > 0.0;" % (table)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    for res in result:
        jobinfo[res[0]] = {}
        jobinfo[res[0]]['CNC'] = int(res[1])
        jobinfo[res[0]]['corehour'] = float(res[2])
        jobinfo[res[0]]['io_volume'] = float(res[3])

        if (int(res[3]) > 0.0):
            jobinfo[res[0]]['avg_mds'] = float(res[4]) / int(res[3])
        else:
            jobinfo[res[0]]['avg_mds'] = 0.0

        jobinfo[res[0]]['pe_r'] = int(res[5])
        jobinfo[res[0]]['pe_w'] = int(res[6])

    remove_job = list()
    for job in IO_mode:
        if (not jobinfo.has_key(job)):
            remove_job.append(job)

    for job in remove_job:
        IO_mode.pop(job)

    for job in jobinfo:
        if (IO_mode.has_key(job)):
            jobinfo[job]['mode'] = IO_mode[job]['mode']
        else:
            jobinfo[job]['mode'] = 'None'

    return jobinfo


def get_job_IOmode_only():

    jobinfo_r = read_IOmode_DB(IOmode_table_read)
    jobinfo_w = read_IOmode_DB(IOmode_table_write)

    IO_mode_r = cal_IOmode_by_volume(jobinfo_r)
    IO_mode_w = cal_IOmode_by_volume(jobinfo_w)

    return IO_mode_r, IO_mode_w


def get_job_bene_info(tag):

    if (tag == 'read'):
        jobinfo = read_IOmode_DB(IOmode_table_read)
    elif (tag == 'write'):
        jobinfo = read_IOmode_DB(IOmode_table_write)
    else:
        print 'Tag must be read or write!'
        sys.exit()

    IO_mode = cal_IOmode_by_volume_NtoN_priv(jobinfo)
    jobinfo = get_perf_info(IO_mode, IOperf_table)

    return jobinfo


def get_job_normal_info(tag):

    if (tag == 'read'):
        jobinfo = read_IOmode_DB(IOmode_table_read)
    elif (tag == 'write'):
        jobinfo = read_IOmode_DB(IOmode_table_write)
    else:
        print 'Tag must be read or write!'
        sys.exit()

    IO_mode = cal_IOmode_by_volume(jobinfo)
    #    jobinfo = get_perf_info(IO_mode, IOperf_table)

    print len(jobinfo)
    return jobinfo


if __name__ == "__main__":

    sum_job, sum_corehour = get_corehour_jobnum()
    get_job_bene_info('read')
    get_job_bene_info('write')
