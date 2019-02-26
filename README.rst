☤ Beacon 
------------

.. image:: https://github.com/Beaconsys/Beacon/blob/master/Beacon_icon.jpg
   :height:: 100px
   :width:: 100px


Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.3 Sunway TaihuLight Supercomputer for over a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

The work is co-operated by Shandong University, Tsinghua University, Qatar Computing Research institute, Emory University and National Supercomputing Center in Wuxi.

We are now cleaning up our codes and gradually open source Beacon code/Data collected on Sunway TaihuLight, including monitoring and analysis methods.

☤ How to use
------------
You can easily to establish Beacon to collect the useful message on other machines.

- Select some nodes to install Beacon backend Database. 
  (Logstash, Redis, Elasticsearch)
- Configuration Example.

  // Collect messages from monitoring programs 
  input {
           file {
                   type => "lala test"
                   path => "/root/testfile"
           }
           file {
                   type => "sys messages"
                   path => "/var/log/messages"
           }
           tcp {
                port => "9999"
                codec => "plain"
           }
           stdin {
           }
  }
  #   output {
  #               stdout {
  #                       codec=>rubydebug
  #               }
  #   }
  output {
          redis {
                  host => 'localhost'
                  data_type => 'list'
                  port => '6379'
                  key => 'logstash:redis'
          }
  }
  
  // Extract message from Redis and store it to the Elasticsearch
  input {
        redis {
                host => 'localhost'
                data_type => 'list'
                port => "6379"
                key => 'logstash:redis'
                type => 'redis-input'
        }
  }
  #output {
  #       stdout {
  #               codec=>rubydebug
  #       }
  #}
  output {
        elasticsearch {
                host=>localhost
                cluster=> "elasticsearch_cluster"
        }
  }
  
  // Use Redis to cache messages
.. code:: python  

  pidfile /var/run/redis.pid
  port 6379
  timeout 0
  loglevel verbose 
  logfile /var/log/redis.log
  dbfilename dump.rdb
  dir /root/ELK/redis/db/
  ## vm-swap-file /tmp/redis.swap
  
You can nearly use the default configuration. 
However, remember to set the same cluster name and ensure these backend nodes are in the same network segment.

☤ sys
------------

Our code will be opened source in this directory, including monitoring module, analysis module and web interface. For more detailed information, just read README in sys directory.

# Analysis_script
------------
In this directory, we will open source our code which is used to analysis these mass data collected by Beacon. There are many subdirectory and you can find their introduction in README in this directory.

. About Analysis_script directory
------------

These scripts are all our scripts to deal with mass data collected by Beacon, including scripts query ES(LWFS, lustre), mysql(job database). We classify these scripts in to serveral categories as you can see some subdirectories in this directory.

. About Job directory
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
 
. About LWFS_client directory
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
        
. About LWFS_server directory
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
        read | write | Meta | wait | exe.csv column is 128 group * 9 columns 9 = nodeip + 8 datas row for time(seconds per row)
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
        
        
. About lustre_client directory
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

. About lustre_server directory
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

. About MDS directory
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


# Monitoring_module
------------
In this directory, we will open source our code which is used to collect data on the Sunway TaihuLight supercomputer, includeing collecting data on compute nodes, forwarding nodes and storages. For more detail information, just read README in this directory.

. About monitoring module directory
------------

In this directory, we plan to open source our code which is used to collect data on supercomputers, including monitoring on compute nodes, forwarding nodes, storage nodes and metadata nodes. We classify these scripts in to serveral categories as you can see some subdirectories in this directory.

- get_lwfs_queue_lantency.py
    (This script is used to collect I/O behavior on LWFS servers (on forwarding nodes))
.. code:: python
        
        python get_lwfs_queue_latency.py
- monitor_LWFS_client
    (This directory including many c files which is used to collect data on compute nodes with an efficient compression method)
.. code:: c
    
        make
        ./a.out -t ES_host -p ES_port /io_behavior
- monitor_lustre_client.py
    (This script is used to collect I/O behavior on lustre clients, including RPC requests)
.. code:: python

        python monitor_lustre_client.py -g
        # -g means collect data from default configuration, for more detail information use -n
- monitor_lustre_server.py
    (This script is used to collect I/O behavior on lustre servers, including OST status)
.. code:: python

        python monitor_lustre_server.py -g
        # -g means collect data from default configuration, for more detail information use -n
- monitor_lustre_MDS.py
    (This script is used to collect I/O behavior on metadata nodes)
.. code:: python

        python monitor_lustr_MDS.py -g
        # -g means collect data from default configuration, for more detail information use -n

# Util
------------ 
In this derictory, we will open source our other util code here.

# Web_interface
------------
In this directory, we will open source our code which is used to show our users a websizte to make Beacon easy-to-use. For more detail inforamtion, just read README in this derectory

. About web interface directory
------------

In this directory, we plan to open source our web code here, including the efficient cache strategy.

- app.py
    (This is the main program entry, to launch our Beacon monitoring application server, please run the following command:)
.. code:: python

        python app.py
- auth
    (This module is used for User Authentication. In our environment, we implement our user authentication based on LDAP. You can custom your own user authentication via modifying the auth.py file)
    
    - user.py
        (This module contains the implementation of the User class used for flask_login module)
    - auth.py
        (You can modify the validate_user() function to custom your own user authentication)
.. code:: python

        def validate_user(username, passwd)    
- static
    (This directory contains the static files for Beacon web applications, including css files, js files, etc.)
- util
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
.. code:: python

        def get_query_para(jobid, stime = '', etime = '')
        def datetime_to_sec(xtime)
        def get_host_ip_list()
        def get_index(stime, etime)           
- templates
    (This directory contains the flask template HTML files.)

☤ data
------------

This directory is used to store open source data. Because data collected by Beacon is mass and we had to put it here, we plan to open source data gradually.

Step to obtain the data:

- We put open source data on cloud
- We share the link here 
- Anyone can obtian these data by access the `link here <https://pan.baidu.com/s/1TasclvmkpqPDHmTTkKMFiQ>`_ with fetchCode ``8pja``

We are now peaparing data and will open source gradually.

Data categories are:(Data format are shown below)

index-name  ||  data-type  ||  id  ||  score  ||  message  ||  @version  ||  @timestamp  ||  host

particularly ：message, timestamp, host

In order to open source the data, we perform a mapping strategy. e.g:

    Original:
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5 => 0x1200bd3f0
    
    After mapping:
    [2018-09-10 14:16:52] T OPEN() /User146/6596814368836924247/-1160749754054947605/-8481035609384531935/2230746621555036977/756880090362066628/-1752974055252976644 =>  0x1200bd3f0
    
By the way, for **open opearation**: There may be two same open opearation in the trace. e.g:
    
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5 => 0x1200bd3f0
    
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5
    
We can find that only one open operation has the file descriptor. The reason for this phenomenon is that one operation is the request initiator without file descriptor, and the other operation has alreadly received the request comletation signal with file descriptor.

Every file or directory will be instead by a hash value. Every User will be instead by "Userxxx"

- ES_COMP
    (Data collected by Beacon from compute nodes node by node)
- ES_FWD1
    (Data collected by Beacon from default forwarding nodes)
- ES_FWD2
    (Data collected by Beacon from rest forwarding nodes)
- ES_MDS
    (Data collected by Beacon from MDS)
- ES_Latency
    (Data collected by Beacon from forwarding nodes, on LWFS servers, including queue length and latency)
- ES_OST1
    (Data collected by Beacon from default storage nodes)
- ES_OST2
    (Data collected by Beacon from rest storage nodes)
- Job
    (Data collected by Beacon from applications running on the TaihuLight) 
    (PS: we are still applying for open sourece this part.)
    
We will continue to open source our data, including many fields.  

Still doing...

Data are gradually put on the clound.


☤ Thank You
-----------

Thanks for checking this library out! I hope you find it useful.
Of course, there's always room for improvement. Feel free to `open an issue <https://github.com/Beaconsys/Beacon/issues>`_ so we can make Beacon better, stronger, faster.

Also, if you have any questions，

contact us:

Email: tianyuzhang1214@163.com.
