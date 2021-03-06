☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

☤ About Analysis_script directory
------------

These scripts are all our scripts to deal with mass data collected by Beacon, including scripts query ES(LWFS, lustre), mysql(job database). We classify these scripts in to serveral categories as you can see some subdirectories in this directory.

☤ About Job directory
------------

First, we introduce job directory for you. You can see four file in this directory.
 
- COMPID_CabinetID 
    (A original statistic mapping table between compute node and forwarding node)
- job_cabid.py 
    (Use this script, you can get the cabinets that are used by the given job)    
.. code:: python
        
        python job_cabid.py JOBID
- job_ip.py
    (This script has many functions, you can obtain jobs' summary running status through this script)
.. code:: python
    
        python job_ip.py time1 time2
        python job_ip.py JOBID
- jobcount_coreutilize.py
    (This script is used to calculate jobs' core-hour, which can also be used to calcute users' cost)
.. code:: python
        
        python jobcount_coreutilize.py time1 time2
 
☤ About LWFS_client directory
------------ 

In this directory, you can find many scripts to operate data on the compute node.

- abnormal_node_detect.py 
   (This script is used to detect abnormal nodes by the given jobid)
.. code:: python
        
        python abnormal_node_detect.py JOBID
        # use jobid list, this script can detect anomaly automatically 
- deal gnenrator.py
    (This script includes many function, is used to deal various messages)
.. code:: python

        def fwd_deal_message(ost_message, ost_time, start_time, end_time)
        def ost_deal_message(ost_message, ost_time, start_time, end_time)
        def deal_part_message(resultr, resultw, result_open, result_close, \
               resltr_ops,resultw_ops, resultr_size, resultw_size, dictr, dictw, \
               results_message, file_open, file_all_set, \
               results_host, min_time, max_time)
        def deal_all_message(results_message, results_host, min_time, max_time)
        def deal_single_message_fd(results_message)
        def deal_single_message(results_message)
- es_search.py 
    (A function, including query body)
.. code:: python

        def search(time_start, time_end, host, index, host_t)
- es_search_fwd.py
    (Query body)
.. code:: python

        def search_interval(time_s, time_e, fwd, host, index, host_t)
- es_search_ost.py
    (Query body)
.. code:: python
        def search_interval(time_s, time_e, host, index, host_t)
- job_ip_all.py
    (This script has many functions, you can obtain jobs' summary running status through this script)
.. code:: python
    
        python job_ip.py time1 time2
        python job_ip.py JOBID
- savejob_jobid_modified.py
    (A function, used to save job's data which has been queried and dealed) 
- scroll_query.py
    (Query body)
- showjob_by_jobid.py
    (This script is used to search job's running status and I/O performance by the given jobid)
.. code:: python
        
        python showjob_by_jobid.py JOBID
- time_to_sec.py
    (A function is used to time transformation)
.. code:: python

        day_time = time.strptime(time_given, '%Y-%m-%d %H:%M:%S')
        def time_to_sec(day_time)
        
☤ About LWFS_server directory
------------

There are 4 files in this directory, including

- data_example.txt
    (data example which is stored in ES)
- create_csv.csv
    (query from ES, store the analysised data into csv files)
.. code:: python
    
        >> define start_time and end_time
        python create_csv.csv
        queue.csv row for time(seconds per row) column for queue value per nodeip
        read | write | Meta ||| wait | exe.csv column is 128 group * 9 columns 9 = nodeip + 8 datas row for time(seconds per row)
- forwarding_each_all.py
    (Query body)
.. code:: python

        def search(time_s, time_e, host, index, host_t)
        def search_le(time_std, host, index, host_t)
        def search_gt(time_std, host, index, host_t)
- deal_latency_queue.py
    (query from ES and deal latency and queue length data)
.. code:: python
    
        >> define start_time and end_time
        python deal_latency_queue.py
        
        
☤ About lustre_client directory
------------ 

There are 5 file in this directory, including

- forwarding_each_all.py
    (Query body)
- lustre_client_band_cache.py
    (This script is used to query lustre client data)
.. code:: python
        
        python lustre_client_band_cache.py time1 time2 vbfs -t -b -c
        vbfs means use reset forwarding nodes, -t represents save trace, -b means get bandwidth, -c means get cache information, more detail information you can use -n
-  draw.py
    (This script is used to visualize)
- compute_band_gio.py
    (This script is used to compute the default forwarding nodes' bandwidth)
- compute_volume.py
    (Compute the total volume)

☤ About lustre_server directory
------------ 

There are 4 file in this directory, including

- OST_each_all.py
    (Query body)
- lustre_server_band.py
    (This script is used to query lustre server data)
.. code:: python
    
        python lustre_server_band_cache.py time1 time2 vbfs -t -d
        -t represents save trace, -d means draw pic, more detail information you can use -n
- draw.py 
    (This script is used to visualize)
- compute_volume.py
    (Compute the total volume)     

☤ About MDS directory
------------ 

There are 3 py files in this directory, including

- lustre_MDS.py
    (This script is used to query metadat from elasticsearch database)
.. code:: python
       
        python lustre_MDS.py time1 time2 -t
        #-t represents save trace, more detail information you can use -n
- query_MDS.py
    (A function, including query body)
- draw.py
   (This script is used to visualize results)

Contact us:   

Email: tianyuzhang1214@163.com.
