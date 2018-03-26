#!/usr/bin/env python

"""
This program is a sequence to get experiment data for the
IC3.


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


if __name__ == '__main__':
    # Extract valid filenames from RIGHT_ROOT
    filename_list = []
    for path, subdirs, files in os.walk(RIGHT_ROOT):
        for filename in files:
            if 'get_right' in filename:
                f = os.path.join(path, filename)
                filename_list.append(f)



    # Read valid reight
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


    # Load old right file
    src = open(RIGHT_PATH, 'r')
    right_list = json.loads(src.read())
    src.close()


    # Test Transaction
    print 'Start testing transaction'

    test_len = len(tmp_right_list)
    print 'test len', test_len

    cnt = 1
    api = Iota('http://localhost:14265')
    for tmp_right in tmp_right_list:
        res = api.find_transactions(tags=[tmp_right['tag']])
        print 'Test Progress: ', cnt, '/', test_len
        cnt += 1

        if len(res['hashes']) != 1:
            continue

        right_list.append(tmp_right)


    # Restore
    src = open(RIGHT_PATH, 'w')
    src.write(json.dumps(right_list))
    src.close()

