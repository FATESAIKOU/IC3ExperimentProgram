#!/usr/bin/env python

"""
This program contains the server needed by the experiment
sequence for the IC3 paper published by FATESAIKOU.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
@argv[1]: service port
@argv[2]: iota node address
@argv[3]: cache mode
@argv[4]: buffer size
"""

from IoTNetworkAgent import IoTServer

import logging
import asyncore
import sys


IOT_CLOUD_KEY = 'EBK9IHE9VAQQNZLGHDXBGAITFHRXAGPAPCOWEGA9GCCLQGHEDPSQYWOTQUSNQUNTVWBQBJYDZTGWZGKBE'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s %(message)s')

    SERVER_PORT    = int(sys.argv[1])
    IOTA_NODE_ADDR = sys.argv[2]
    CACHE_MODE     = (sys.argv[3] == 'True')
    BUFFER_SIZE    = int(sys.argv[4])

    iot_server = IoTServer(
        server_addr_pair=('localhost', SERVER_PORT),
        iot_cloud_key=IOT_CLOUD_KEY,
        iota_node_addr=IOTA_NODE_ADDR,
        cache_mode=CACHE_MODE,
        buffer_size=BUFFER_SIZE
    )

    asyncore.loop()
