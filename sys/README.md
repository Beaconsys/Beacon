# Introduction of sys code
## 1 Analysis_script
In this directory, we will open source our code which is used to analysis these mass data collected by Beacon. There are many subdirectory and you can find their introduction in README in this directory.

### 1.1 Analysis_script directory
These scripts are all our scripts to deal with mass data collected by Beacon, including scripts query ES(LWFS, lustre), mysql(job database). We classify these scripts in to serveral categories as you can see some subdirectories in this directory.

### 1.2 Job directory
First, we introduce job directory for you. You can see four file in this directory.
* COMPID_CabinetID 
    (A original statistic mapping table between compute node and forwarding node)
* job_cabid.py 
    (Use this script, you can get the cabinets that are used by the given job)            
  > python job_cabid.py JOBID
* job_ip.py
    (This script has many functions, you can obtain jobs' summary running status through this script)    
  > python job_ip.py time1 time2
  
  > python job_ip.py JOBID
* jobcount_coreutilize.py
    (This script is used to calculate jobs' core-hour, which can also be used to calcute users' cost)
  > python jobcount_coreutilize.py time1 time2
 
### 1.3 LWFS_client directory
In this directory, you can find many scripts to operate data on the compute node.

* abnormal_node_detect.py 
   (This script is used to detect abnormal nodes by the given jobid) 
  > python abnormal_node_detect.py JOBID `# use jobid list, this script can detect anomaly automatically`
* deal gnenrator.py
    (This script includes many function, is used to deal various messages)
````
    def fwd_deal_message(ost_message, ost_time, start_time, end_time)
    def ost_deal_message(ost_message, ost_time, start_time, end_time)
    def deal_part_message(resultr, resultw, result_open, result_close,
           resltr_ops,resultw_ops, resultr_size, resultw_size, dictr, dictw,
           results_message, file_open, file_all_set,
           results_host, min_time, max_time)
    def deal_all_message(results_message, results_host, min_time, max_time)
    def deal_single_message_fd(results_message)
    def deal_single_message(results_message)
````
* es_search.py 
    (A function, including query body)
    `def search(time_start, time_end, host, index, host_t)`
* es_search_fwd.py
    (Query body)
    `def search_interval(time_s, time_e, fwd, host, index, host_t)`
* es_search_ost.py
    (Query body)
    `def search_interval(time_s, time_e, host, index, host_t)`
* job_ip_all.py
    (This script has many functions, you can obtain jobs' summary running status through this script)
  > python job_ip.py time1 time2
  
  > python job_ip.py JOBID
* savejob_jobid_modified.py
    (A function, used to save job's data which has been queried and dealed) 
* scroll_query.py
    (Query body)
* showjob_by_jobid.py
    (This script is used to search job's running status and I/O performance by the given jobid)
  > python showjob_by_jobid.py JOBID
* time_to_sec.py
    (A function is used to time transformation)
```
    day_time = time.strptime(time_given, '%Y-%m-%d %H:%M:%S')
    def time_to_sec(day_time)
```        
### 1.4 LWFS_server directory
There are 4 files in this directory, including

* data_example.txt
    (data example which is stored in ES)
* create_csv.csv
    (query from ES, store the analysised data into csv files)      
  > python create_csv.csv
```  
  # define start_time and end_time
  # queue.csv row for time(seconds per row) column for queue value per nodeip
  # read | write | Meta | wait | exe.csv column is 128 group * 9 columns 9 = nodeip + 8 datas row for time(seconds per row)
```  
* forwarding_each_all.py
    (Query body)
```
    def search(time_s, time_e, host, index, host_t)
    def search_le(time_std, host, index, host_t)
    def search_gt(time_std, host, index, host_t)
```
* deal_latency_queue.py
    (query from ES and deal latency and queue length data)
  > python deal_latency_queue.py `# define start_time and end_time`       
        
### 1.5 Lustre_client directory
There are 5 file in this directory, including

* forwarding_each_all.py
    (Query body)
* lustre_client_band_cache.py
    (This script is used to query lustre client data)       
  > python lustre_client_band_cache.py time1 time2 vbfs -t -b -c `# vbfs means use reset forwarding nodes, -t represents save trace, -b means get bandwidth, -c means get cache information, more detail information you can use -n`
* draw.py
    (This script is used to visualize)
* compute_band_gio.py
    (This script is used to compute the default forwarding nodes' bandwidth)
* compute_volume.py
    (Compute the total volume)

### 1.6 Lustre_server directory
There are 4 file in this directory, including

* OST_each_all.py
    (Query body)
* lustre_server_band.py
    (This script is used to query lustre server data)
  > python lustre_server_band_cache.py time1 time2 vbfs -t -d `# -t represents save trace, -d means draw pic, more detail information you can use -n`
* draw.py 
    (This script is used to visualize)
* compute_volume.py
    (Compute the total volume)     

### 1.7 MDS directory
There are 3 py files in this directory, including

* lustre_MDS.py
    (This script is used to query metadat from elasticsearch database)
  > python lustre_MDS.py time1 time2 -t `#-t represents save trace, more detail information you can use -n`
* query_MDS.py
    (A function, including query body)
* draw.py
   (This script is used to visualize results)

## 2 Monitoring_module
In this directory, we will open source our code which is used to collect data on the Sunway TaihuLight supercomputer, includeing collecting data on compute nodes, forwarding nodes and storages. For more detail information, just read README in this directory.

### 2.1 Monitoring module directory
In this directory, we plan to open source our code which is used to collect data on supercomputers, including monitoring on compute nodes, forwarding nodes, storage nodes and metadata nodes. We classify these scripts in to serveral categories as you can see some subdirectories in this directory.

* get_lwfs_queue_lantency.py
    (This script is used to collect I/O behavior on LWFS servers (on forwarding nodes))
  > python get_lwfs_queue_latency.py
* monitor_LWFS_client
    (This directory including many c files which is used to collect data on compute nodes with an efficient compression method)
  > make
  
  > ./a.out -t ES_host -p ES_port /io_behavior
* monitor_lustre_client.py
    (This script is used to collect I/O behavior on lustre clients, including RPC requests)
  > python monitor_lustre_client.py -g `# -g means collect data from default configuration, for more detail information use -n`
* monitor_lustre_server.py
    (This script is used to collect I/O behavior on lustre servers, including OST status)
  > python monitor_lustre_server.py -g `# -g means collect data from default configuration, for more detail information use -n`
* monitor_lustre_MDS.py
    (This script is used to collect I/O behavior on metadata nodes)
  > python monitor_lustr_MDS.py -g `# -g means collect data from default configuration, for more detail information use -n`

## 3 Util
In this derictory, we will open source our other util code here.

## 4 Web_interface
In this directory, we will open source our code which is used to show our users a websizte to make Beacon easy-to-use. For more detail inforamtion, just read README in this derectory

### 4.1 Web interface directory
In this directory, we plan to open source our web code here, including the efficient cache strategy.
* app.py
    (This is the main program entry, to launch our Beacon monitoring application server, please run the following command:)
  > python app.py
* auth
    (This module is used for User Authentication. In our environment, we implement our user authentication based on LDAP. You can custom your own user authentication via modifying the auth.py file)    
    - user.py
        (This module contains the implementation of the User class used for flask_login module)
    - auth.py
        (You can modify the validate_user() function to custom your own user authentication)
        ```
        def validate_user(username, passwd)
        ```
* static
    (This directory contains the static files for Beacon web applications, including css files, js files, etc.)
* util
    (This module contains utility tools and methods, including database access, data caching, auxiliary tools, etc.)
    
    - db_util.py
        (This module contains all the database access methods.)
    - cache_cn.py
        (This module is used for caching the webpage plot data in order to improve user querying experience.)
    - lwfs_client.py
        (This module querys monitoring data for the compute nodes. So far, this module can query and analyze read or write I/O bandwidth, IOPS and file open/close count data.)
    - fwd.py
        (This module querys monitoring data for the forwarding nodes. So far, this module only query analyze data for I/O bandwidth on forwarding nodes.)
    - lustre_ost.py
        (This module querys monitoring data for the OST bandwidth.)
    - util.py
        (This module contains the auxiliary methods used for other modules, some examples are as follows:)
        ```
        def get_query_para(jobid, stime = '', etime = '')
        def datetime_to_sec(xtime)
        def get_host_ip_list()
        def get_index(stime, etime)
        ```
* templates
    (This directory contains the flask template HTML files.)
