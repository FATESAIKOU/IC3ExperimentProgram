#!/usr/bin/env python

"""
This program is a sequence to extract experiment data for the
IC3.


@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/20/2018
@argv[1]: data root
@argv[2]: data restore path
"""

import sys
import os
import json
import re

from pprint import pprint

DATA_ROOT         = sys.argv[1]
DATA_RESTORE_PATH = sys.argv[2]


def getData(filename):
    src = open(filename, 'r')
    obj = json.loads(src.read())
    src.close()

    return [l['delay'] for l in obj['content']]


def getExtractedData(data_root):
    data_list = {
        'get_right': {},
        'get_access': {}
    }

    for path, subdirs, files in os.walk(data_root):
        for filename in files:
            # Extract file info
            act, ts, cm, bs, _ = re.split('-|\.', filename)
            f = os.path.join(path, filename)
            datas = getData(f)

            # Check key exist or not
            if act == 'get_right':
                update_key = "%s-%s" % (ts, bs)
            else:
                update_key = "%s-%s" % (ts, cm)

            if update_key not in data_list[act].keys():
                data_list[act].update({update_key: []})
            
            # update
            data_list[act][update_key].append(datas)
   
    return data_list


def restore(data_list, data_restore_path):
    src = open(data_restore_path, 'r')
    ori_data_list = json.loads(src.read())
    src.close()

    for act in ['get_right', 'get_access']:
        for k in data_list[act].keys():
            if k in ori_data_list[act].keys():
                ori_data_list[act][k].extend(data_list[act][k])
            else:
                ori_data_list[act].update({k: data_list[act][k]})
    
    src = open(data_restore_path, 'w')
    src.write(json.dumps(ori_data_list))
    src.close()


if __name__ == '__main__':
    print DATA_ROOT
    print DATA_RESTORE_PATH

    data_list = getExtractedData(DATA_ROOT)
    pprint(data_list)
    restore(data_list, DATA_RESTORE_PATH)
