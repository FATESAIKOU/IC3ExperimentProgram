#!/usr/bin/env python

"""
This program contains the server needed by the experiment
sequence for the IC3 paper published by FATESAIKOU.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
"""

from IoTNetworkAgent import IoTServer

import logging
import asyncore


IOT_CLOUD_KEY = 'EBK9IHE9VAQQNZLGHDXBGAITFHRXAGPAPCOWEGA9GCCLQGHEDPSQYWOTQUSNQUNTVWBQBJYDZTGWZGKBE'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s %(message)s')

    iot_server = IoTServer(
        server_addr_pair=('localhost', 8079),
        iot_cloud_key=IOT_CLOUD_KEY,
        iota_node_addr='http://localhost:14265',
        cache_mode=True,
        buffer_size=256
    )

    asyncore.loop()
