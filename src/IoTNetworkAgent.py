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

from TxLib import TxHandler

import asyncore
import logging
import socket
import json
import time
import string
import random


def getID(length):
    candidates = string.ascii_uppercase + '9'
 
    return ''.join([random.choice(candidates) for _ in xrange(length)])
 

def createClients(server_addr_pair, action, fail_prop, number, right_file='./right.json'):
    src = open(right_file, 'r')
    valid_leases = json.loads(src.read())
    src.close()

    if action == 'get_right':
        s_time = time.time()
        e_time = s_time + 1

        leases = [
            {
                'device_key': getID(81),
                'accessor_key': getID(81),
                's_time': s_time,
                'e_time': e_time
            }
            for _ in xrange(number)
        ]
        
        valid_leases.extend(leases)
        src = open(right_file, 'w')
        src.write(json.dumps(valid_leases))
        src.close()

        aim_leases = leases # extend?
    elif action == 'get_access':
        aim_leases = random.sample(valid_leases, number)

    clients = [
        IoTClient(
            server_addr_pair,
            json.dumps({
                'cmd': action,
                'content': lease
            })
        )
        for lease in aim_leases
    ]

    return clients


"""
Client Side Agent
"""

class IoTClient(asyncore.dispatcher):
    """
    Sends messages to the server and receives responses.
    """

    def __init__(self, server_addr_pair, message, chunk_size=4096):
        # define logger & message to send.
        self.logger = logging.getLogger('\033[43m[Client]\033[49m')
        self.message = message
        self.to_send = message
        self.logger.debug('message: %s', message)
        self.chunk_size = chunk_size

        # a space to restore the responses
        self.received_data = []

        # init socket
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', server_addr_pair)
        self.connect(server_addr_pair)

        # result
        self.status = 'pending'
        self.delay  = 0.0


    def handle_connect(self):
        self.logger.debug('\033[92m[HANDLE_CONNECT]\033[37m handle_connect()')


    def handle_close(self):
        self.delay = self.e_time - self.s_time
        self.logger.debug('\033[92m[HANDLE_CLOSE]\033[37m handle_close()')
        self.close()

        received_message = ''.join(self.received_data)
        if 'ERROR' in received_message:
            self.status = 'ERROR'
        else:
            self.status = 'SUCCESS'


    def writable(self):
        self.logger.debug('\033[94m[DETECT_WRITABLE]\033[37m writable() -> %s', len(self.to_send) > 0)
        return (len(self.to_send) > 0)


    def handle_write(self):
        self.s_time = time.time()
        sent_len = self.send(self.to_send[:self.chunk_size])
        self.logger.debug('\033[93m[HANDLE_WRITE]\033[37m handle_write() -> (%d) "%s"', sent_len, self.to_send[:sent_len])
        self.to_send = self.to_send[sent_len:]


    def handle_read(self):
        data = self.recv(self.chunk_size)
        self.e_time = time.time()
        self.logger.debug('\033[93m[HANDLE_READ]\033[37m handle_read() -> (%d) "%s"', len(data), data)
        self.received_data.append(data)

"""
Server Side Agent
"""

class IoTServer(asyncore.dispatcher):
    """
    Receives connections and establishs handlers for each client
    """

    def __init__(self, server_addr_pair, iot_cloud_key, iota_node_addr, cache_mode, buffer_size):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger('\033[104m[SERVER]\033[49m')

        # init server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(server_addr_pair)
        self.logger.debug('binding to %s', self.getsockname())
        
        # init TxHandler
        self.txh = TxHandler(
            iot_cloud_key, cache_mode, buffer_size, iota_node_addr
        )

        # start service
        self.listen(1024)


    def handle_accept(self):
        connection = self.accept()
        self.logger.debug('\033[92m[HANDLE_ACCEPT]\033[37m handle_accept() -> %s', connection[1])
        IoTRequestHandler(server=self, sock=connection[0], tx_handler=self.txh)


    def handle_close(self):
        self.logger.debug('\033[92m[HANDLE_CLOSE]\033[37m handle_close()')
        self.close()


class IoTRequestHandler(asyncore.dispatcher):
    """
    Handle request message from single client
    """

    def __init__(self, server, sock, tx_handler, chunk_size=4096):
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

        if not (self.writable()):
            self.handle_close()


    def handle_close(self):
        self.logger.debug('\033[92m[HANDLE_CLOSE]\033[37m handle_close()')
        self.close()


    def get_right(self, r_info):
        if not self.txh.checkRegistable(
                r_info['device_key'],
                r_info['accessor_key'],
                float(r_info['s_time']), 
                float(r_info['e_time'])
            ):
            return '[ERROR] Permission is not registable.'
        
        self.txh.registPermission(
            r_info['device_key'], r_info['accessor_key'],
            r_info['s_time'], r_info['e_time']
        )

        return '[INFO] Permission registed successfully.'

    
    def get_access(self, r_info):
        if self.txh.checkPermission(
                r_info['device_key'], 
                r_info['accessor_key'], 
                float(r_info['s_time']), 
                float(r_info['e_time'])
            ):
            return '[INFO] Got access successfully.'
        else:
            return '[ERROR] Fault to get access.'
