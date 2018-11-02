☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

☤ About web interface directory
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
    
   
Contact us:   

Email: tianyuzhang1214@163.com.
