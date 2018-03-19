"""
There are 3 classes in this file:

    - IoTServer: A class to accept request from outside.

    - IoTRequestHandler: A class to handle the socket
        generated after accepting a request by IoTServer.

    - Client: An agent for establishing a request to
        IoTServer.


and all of these would operate synchronously.


@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
"""

#from TxLib import TxHandler

import asyncore
import logging
#import socket
import json


class IoTRequestHandler(asyncore.dispatcher):
    """
    Handle request message from single client
    """

    def __init__(self, server, sock, tx_handler, chunk_size=256):
        self.server = server
        self.txh = tx_handler
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('\033[46m[HANDLER(%s)]\033[49m' % str(sock.getsockname()))
        asyncore.dispatcher.__init__(self, sock=sock)
        self.data_to_write = []


    def writable(self):
        is_writable = (len(self.data_to_write) > 0)
        self.logger.debug('\033[94m[DETECT_WRITABLE]\033[37m writable() -> %s', is_writable)

        return is_writable


    def handle_read(self):
        raw_request = self.recv(self.chunk_size)

        self.logger.debug('\033[93m[HANDLE_READ]\033[37m handle_read() -> (%d) "%s"', len(raw_request), raw_request)

        request = json.loads(raw_request)

        if request['cmd'] == 'shutdown':
            self.server.handle_close()
            self.handle_close()
        elif request['cmd'] == 'get_right':
            data = self.get_right(request['content']) 
        elif request['cmd'] == 'get_access':
            data = self.get_access(request['content'])
        else:
            data = '[ERROR] unknown command'

        self.data_to_write.insert(0, data)

    
    def handle_write(self):
        response = self.data_to_write.pop()
        sent_len = self.send(response[:self.chunk_size])

        if sent_len < len(response):
            remaining = response[:sent_len]
            self.data_to_write.append(remaining)

        self.logger.debug('\033[93m[HANDLE_WRITE]\033[37m handle_write() -> (%d) "%s"', sent_len, response[:sent_len])

        if not (self.writable):
            self.handle_close()


    def handle_close(self):
        self.logger.debug('\033[92m[HANDLE_CLOSE]\033[37m handle_close()')
        self.close()


    def get_right(self, r_info):
        if not self.txh.checkRegistable(
                r_info['device_key'],
                r_info['accessor_key'],
                r_info['s_time'], 
                r_info['e_time']
            ):
            return '[Info] Permission is not registable.'
        
        self.txh.registPermission(
            r_info['device_key'], r_info['accessor_key'],
            r_info['s_time'], r_info['e_time']
        )

        return '[Info] Permission registed successfully.'

    
    def get_access(self, r_info):
        if self.txh.checkPermission(
                r_info['device_key'], 
                r_info['accessor_key'], 
                r_info['s_time'], 
                r_info['e_time']
            ):
            return '[Info] Got access successfully.'
        else:
            return '[Info] Fault to get access.'
