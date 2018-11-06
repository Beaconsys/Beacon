☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for over a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

We are now cleaning up our codes and gradually open source Beacon code/Data collected on Sunway TaihuLight, including monitoring and analysis methods.

☤ sys
------------

Our code will be opened source in this directory, including monitoring module, analysis module and web interface. For more detailed information, just read README in sys directory.

☤ data
------------

This directory is used to store open source data. Because data collected by Beacon is mass and we had to put it here, we plan to open source data gradually.

Step to obtain the data:

- We put open source data on cloud
- We share the link here 
- Anyone can obtian these data by access the `link here <https://pan.baidu.com/s/1TasclvmkpqPDHmTTkKMFiQ>`_ with fetchCode ``8pja``

We are now peaparing data and will open source gradually.

Data categories are:

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
  - ES_network
    (Data collected by Beacon from IB switches)

☤ Thank You
-----------

Thanks for checking this library out! I hope you find it useful.
Of course, there's always room for improvement. Feel free to `open an issue <https://github.com/Beaconsys/Beacon/issues>`_ so we can make Beacon better, stronger, faster.

Also, if you have any questions，

contact us:

Email: tianyuzhang1214@163.com.
