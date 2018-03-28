#!/usr/bin/env python

"""
This program is a sequence to extract right for the IC3.


@author : FATESAIKOU
@email  : qzsecftbhhhh@gmail.com
@date   : 03/20/2018
@argv[1]: right root
@argv[2]: right path to restore
"""

import sys
import json
import os

from iota import Iota

IOT_CLOUD_KEY = 'EBK9IHE9VAQQNZLGHDXBGAITFHRXAGPAPCOWEGA9GCCLQGHEDPSQYWOTQUSNQUNTVWBQBJYDZTGWZGKBE'

RIGHT_ROOT = sys.argv[1]
RIGHT_PATH = sys.argv[2]


def readRight(filename_list, right_path):
    # Read valid right
    tmp_right_list = []
    for filename in filename_list:
        src = open(filename, 'r')
        rights = json.loads(src.read())
        src.close()
        
        for r in rights:
            r.update({
                'tag': r['device_key'][:14] + IOT_CLOUD_KEY[:13],
            })

            tmp_right_list.append(r)
    
    tmp_right_list_set = set([json.dumps(t) for t in tmp_right_list])


    # Load old right file
    src = open(right_path, 'r')
    right_list = json.loads(src.read())
    src.close()
    right_list_set = set([json.dumps(t) for t in right_list])

    new_right_list_set = tmp_right_list_set - right_list_set
    new_right_list = [json.loads(n) for n in new_right_list_set]

    return [new_right_list, right_list]


if __name__ == '__main__':
    print "Rights Root:", RIGHT_ROOT
    print "Rights Path:", RIGHT_PATH

    # Extract valid filenames from RIGHT_ROOT
    filename_list = []
    for path, subdirs, files in os.walk(RIGHT_ROOT):
        for filename in files:
            if 'get_right' in filename:
                f = os.path.join(path, filename)
                filename_list.append(f)


    # Read right
    new_right_list, right_list = readRight(filename_list, RIGHT_PATH)


    # Test Transaction
    print 'Start testing transaction'

    test_len = len(new_right_list)
    print 'test len', test_len

    cnt = 0
    r_cnt = 0
    api = Iota('http://localhost:14265')
    for new_right in new_right_list:
        res = api.find_transactions(tags=[new_right['tag']])
        print 'Test Progress: ', r_cnt, '/', cnt, '/', test_len
        cnt += 1

        if len(res['hashes']) != 1:
            continue

        r_cnt += 1
        right_list.append(new_right)


    # Restore
    src = open(RIGHT_PATH, 'w')
    src.write(json.dumps(right_list))
    src.close()

