#!/usr/bin/env python

"""
This program is for rights loading.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
@argv[1]: right file
@argv[2]: load size
@argv[3]: chunk size
@argv[3]: server address
@argv[4]: server port
"""

import asyncore
import logging
import sys
import json

from IoTNetworkAgent import IoTClient


RIGHT_FILE  = sys.argv[1]
LOAD_SIZE   = int(sys.argv[2])
CHUNK_SIZE  = int(sys.argv[3])
SERVER_ADDR = sys.argv[4]
SERVER_PORT = int(sys.argv[5])


def getRightsChunks(right_file_path, load_size, chunk_size):
    src = open(right_file_path, 'r')
    rights = json.loads(src.read())
    src.close()

    if load_size > rights:
        raise IndexError('Load_size is bigger than the rights_file\'s size.')

    for i in range(0, load_size, chunk_size):
        yield rights[i:min(i + chunk_size, load_size)]


def createLoadRightClients(server_addr_pair, rights):
    clients = [
        IoTClient(
            server_addr_pair,
            json.dumps({
                'cmd': 'get_access',
                'content': lease
            })
        )
        for lease in rights
    ]

    return clients


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(name)s %(message)s')


    for rights_chunk in getRightsChunks(RIGHT_FILE, LOAD_SIZE, CHUNK_SIZE):
        clients = createLoadRightClients((SERVER_ADDR, SERVER_PORT), rights_chunk)
        asyncore.loop()
