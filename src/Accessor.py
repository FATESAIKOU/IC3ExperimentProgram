#!/usr/bin/env python

"""
This program contains the experiment sequence for the IC3
paper published by FATESAIKOU. You can choose the type of
experiment, by using proper keyword to pass in:

    - get_right

    - get_access

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
@argv[1]: action
@argv[2]: fail prop
@argv[3]: test size
@argv[4]: cache mode
@argv[5]: buffer size
@argv[6]: log path
@argv[7]: right file
@argv[8]: server address
@argv[9]: server port
@argv[10]: shutdown or not
"""

import asyncore
import logging
import sys
import json

from IoTNetworkAgent import createClients


ACTION      = sys.argv[1]
FAIL_PROP   = float(sys.argv[2])
TEST_SIZE   = int(sys.argv[3])
CACHE_MODE  = (sys.argv[4] == 'True')
BUFFER_SIZE = int(sys.argv[5])
LOG_PATH    = sys.argv[6]
RIGHT_FILE  = sys.argv[7]
SERVER_ADDR = sys.argv[8]
SERVER_PORT = int(sys.argv[9])
SHUTDOWN    = (sys.argv[10] == 'True')


def createLog(clients, log_path, action):
    result = {
        'config': {
            'action': ACTION,
            'fail_prop': FAIL_PROP,
            'test_size': TEST_SIZE,
            'cache_mode': CACHE_MODE,
            'BUFFER_SIZE': BUFFER_SIZE
        },
        'content': []
    }

    for c in clients:
        tmp_r = {
            'action': action,
            'status': c.status,
            'delay': c.delay
        }
        result['content'].append(tmp_r)

    src = open(log_path, 'w')
    src.write(json.dumps(result))
    src.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(name)s %(message)s')


    clients = createClients((SERVER_ADDR, SERVER_PORT), ACTION, FAIL_PROP, TEST_SIZE, RIGHT_FILE)
    asyncore.loop()

    createLog(clients, LOG_PATH, ACTION)

    if SHUTDOWN:
        shutdown_client = createClients((SERVER_ADDR, SERVER_PORT), 'shutdown', 0, 1)
        asyncore.loop()
