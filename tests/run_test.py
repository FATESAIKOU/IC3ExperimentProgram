#!/usr/bin/env python

"""
This program is a sequence to get experiment data for the
IC3.


@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/20/2018
@argv[1]: config path
"""

import sys
import json
import os


CONFIG_PATH = sys.argv[1]

def genString(a, ts, cm, bs, log_path, right_path, s_addr, s_port, i_addr, shutdown):
    if a == 'get_right':
        result = [
            "../src/IoTCluster.py %s %s %s %s &" %\
                (s_port, i_addr, cm, bs),
            "../src/Accessor.py %s 0 %s %s %s %s %s %s %s %s" %\
                (a, ts, cm, bs, log_path, right_path, 
                    s_addr, s_port, shutdown)
        ]
    elif a == 'get_access':
        result = [
            "../src/IoTCluster.py %s %s %s %s &" %\
                (s_port, i_addr, cm, ts + 16),
            "../src/Accessor.py %s 0 %s %s %s %s %s %s %s %s" %\
                (a, ts, cm, bs, log_path, 'right_list.json', 
                    s_addr, s_port, shutdown),
        ]
        if cm == True:
            result.insert(1, 
                "../src/LoadRights.py %s %s %s %s %s" %\
                    ('right_list.json', str(ts), str(10), s_addr, s_port)
            )
    else:
        result = []

    return result
        

def generateTestStrings(cfg):
    log_root   = cfg['log_root']
    right_root = cfg['right_root']
    s_addr     = cfg['server_address']
    s_port     = cfg['server_port']
    i_addr     = cfg['iota_node_address']
    shutdown   = str(cfg['shutdown'])

    test_strings = []
    for cm in cfg['cache_mode']:
        for bs in cfg['buffer_size']:
            for ts in cfg['test_size']:
                for a in cfg['action']:
                    log_path = log_root + "/%s-%s-%s-%s.json" %\
                            (a, ts, cm, bs)

                    right_path = right_root + "/%s-%s-%s-%s.json" %\
                            (a, ts, cm, bs)
                    
                    os.system("echo '[]' > %s" % (right_path))


                    test_strings.append(genString(
                        a, ts, cm, bs,
                        log_path, right_path,
                        s_addr, s_port, i_addr, shutdown
                    ))

    return test_strings


if __name__ == '__main__':
    src = open(CONFIG_PATH, 'r')
    cfg = json.loads(src.read())
    src.close()

    test_strings = generateTestStrings(cfg)
    for cmd_list in test_strings:
        print 'Start round'

        for cmd in cmd_list:
            print cmd
            os.system(cmd)
            os.system('sleep 2')

        print 'End of round'


    print "End Of Experiment"
