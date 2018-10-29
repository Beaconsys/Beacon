☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

☤ About monitoring module directory
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

Contact us:   
Email: tianyuzhang1214@163.com.
