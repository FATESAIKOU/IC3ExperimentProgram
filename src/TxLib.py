"""
This file is an implementation of TxDB, it demonstrates 
the simplest prototype of buffering Transaction before
attachToTangle and caching it for hight speed searching.

@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/18/2018
"""


import json

from iota import Iota, TryteString, Tag, Address
from iota import Transaction, ProposedTransaction
from iota import ProposedBundle

from iota.crypto.signing import KeyGenerator


MY_KEY = 'DFHKERITBIESCMCGKCMKY9QGASSATEQODUPHGZZVONSOTJGCYM9TAUL9ARMYYEMSGNDQUUY9YQYYAZKKE'

# A handler for transaction related request
class TxHandler:

    def __init__(self, cloud_key, cache_mode, buffer_size, iota_node_addr):
        self.tx_cache = []
        self.tx_buffer = []
       
        self.cloud_key = cloud_key
        self.cache_mode = cache_mode
        self.buffer_count = 0
        self.buffer_size = buffer_size

        self.iota_api = Iota(iota_node_addr)


    def checkRegistable(self, device_key, accessor_key, s_time, e_time):
        if self.cache_mode is True:
            tx_datas = self.__filter__(
                self.tx_cache,
                device_key,
                s_time,
                e_time
            )

            if len(tx_datas) > 0:
                return False
            
        tx_tryte_list = self.__getTxWithTag__(device_key, self.cloud_key)

        if len(tx_tryte_list) > 0:
            tx_datas = self.__extract__(tx_tryte_list)
            self.tx_cache.extend(tx_datas)
            return False
        
        return True

                
    def registPermission(self, device_key, accessor_key, s_time, e_time):
        tx_data = {
            'device_key': device_key,
            'accessor_key': accessor_key,
            'cloud_key': self.cloud_key,
            's_time': s_time,
            'e_time': e_time
        }

        self.tx_buffer.append(tx_data)
        self.tx_cache.append(tx_data)
        self.buffer_count += 1

        if not (self.buffer_count < self.buffer_size):
            self.__syncTransaction__(
                self.__createBundle__(self.tx_buffer)
            )
            self.tx_buffer = []
            self.buffer_count = 0

    
    # Check if the permission is avaliable or not?
    def checkPermission(self, device_key, accessor_key, s_time, e_time):
        if self.cache_mode is True:
            tx_datas = self.__filter__(
                self.tx_cache,
                device_key,
                s_time,
                e_time
            )
            
            for tx_data in tx_datas:
                if tx_data['accessor_key'] == accessor_key:
                    return True

        tx_tryte_list = self.__getTxWithTag__(device_key, self.cloud_key)
        
        if not (len(tx_tryte_list) > 0):
            return False
        
        tx_datas = self.__extract__(tx_tryte_list)
        self.tx_cache.extend(tx_datas)

        for tx_data in tx_datas:
            if tx_data['accessor_key'] == accessor_key:
                return True

        return False
        
       
    """
    Private Toolkit
    """
    def __getTxWithTag__(self, device_key, cloud_key):
        tx_hashes = self.iota_api.find_transactions(tags=[
            unicode(device_key[:14] + cloud_key[:13])
        ])['hashes']

        if not (len(tx_hashes) > 0):
            return []

        tx_tryte_list = self.iota_api.get_trytes(hashes=tx_hashes)['trytes']

        return tx_tryte_list


    def __extract__(self, tx_tryte_list):
        tx_contains = [Transaction.from_tryte_string(tryte) for tryte in tx_tryte_list]

        tx_datas = [
            json.loads(tx.signature_message_fragment.decode())
            for tx in tx_contains
        ]
        
        return tx_datas


    def __filter__(self, tx_datas, device_key, s_time, e_time):
        if not (s_time < e_time):
            return []

        tx_filtered_datas = [
            tx_data
            for tx_data in tx_datas
            if tx_data['s_time'] < e_time and tx_data['e_time'] > s_time \
                    and tx_data['device_key'] == device_key
        ]

        return tx_filtered_datas


    def __syncTransaction__(self, bundle):
        approvee_tx = self.iota_api.get_transactions_to_approve(depth=27)
        result = self.iota_api.attach_to_tangle(
            branch_transaction = approvee_tx['branchTransaction'],
            trunk_transaction = approvee_tx['trunkTransaction'],
            min_weight_magnitude = 18,
            trytes = bundle.as_tryte_strings()
        )

        tx_tryte_list = result['trytes']
        self.iota_api.broadcast_and_store(trytes=tx_tryte_list)
    

    def __createBundle__(self, tx_datas):
        # Create Transactions
        tx_list = []
        for tx_data in tx_datas:
            tx = ProposedTransaction(
                address = Address(MY_KEY),
                message = TryteString.from_unicode(json.dumps(tx_data)),
                tag     = Tag(
                            tx_data['device_key'][:14] + tx_data['cloud_key'][:13]
                        ),
                value   = 0
            )

            tx_list.append(tx)
        
        # Create bundle time transaction
        bundle = ProposedBundle()
        for tx in tx_list:
            bundle.add_transaction(tx)
        
        bundle.finalize()
        bundle.sign_inputs(KeyGenerator(MY_KEY))

        return bundle

