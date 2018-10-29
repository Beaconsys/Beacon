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
    (This script is used to calculate jobs' core-hour, which can also be used to calcute users' cost.
    .. code:: python
        
        python jobcount_coreutilize.py time1 time2
 
☤ About LWFS_client directory
------------ 
 
☤ About LWFS_server directory
------------ 

☤ About lustre_client directory
------------ 

☤ About LWFS_server directory
------------ 

☤ About MDS directory
------------ 

  
 
