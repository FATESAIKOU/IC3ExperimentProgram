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
"""

import asyncore
import logging
import sys

from IoTNetworkAgent import createClients

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(name)s %(message)s')

    createClients(('localhost', 8079), sys.argv[1], 0, 10)
    asyncore.loop()

