#!/usr/bin/env python

"""
This program contains the server needed by the experiment
sequence for the IC3 paper published by FATESAIKOU.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
"""

from IoTNetworkAgent import getID
from IoTNetworkAgent import IoTServer

import logging
import asyncore


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s %(message)s')

    iot_server = IoTServer(
        server_addr_pair=('localhost', 8079),
        iot_cloud_key=getID(81),
        iota_node_addr='http://localhost:14265',
        cache_mode=True,
        buffer_size=10
    )

    asyncore.loop()
