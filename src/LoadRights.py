#!/usr/bin/env python

"""
This program is for rights loading.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
@argv[1]: right file
@argv[2]: server address
@argv[3]: server port
"""

import asyncore
import logging
import sys
import json

from IoTNetworkAgent import createClients


RIGHT_FILE  = sys.argv[1]
SERVER_ADDR = sys.argv[2]
SERVER_PORT = int(sys.argv[3])


def checkRightsLen(right_file_path):
    src = open(right_file_path, 'r')
    rights = json.loads(src.read())
    src.close()
    
    return len(rights)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(name)s %(message)s')


    clients = createClients((SERVER_ADDR, SERVER_PORT), 'get_access', 0, checkRightsLen(RIGHT_FILE), RIGHT_FILE)
    asyncore.loop()
