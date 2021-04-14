#!/usr/bin/env python3

import os
import argparse
import json
import numpy as np

parser = argparse.ArgumentParser(
    description='This programme count the number of different tokenids (including epsilon) in the auxiliary sequences from a dump dir.')

parser.add_argument('-d', '--dir', help='The path of the dump dir.', type=str)

args = parser.parse_args()

if __name__ == '__main__':
    dir = args.dir
    with open(os.path.join(dir, 'data.json')) as f:
        data = json.load(f)
    utts = data['utts']
    tokenid2num = dict()
    tokenid2num['0'] = 0
    epsilon_sum = 0
    token_sum = 0
    for key in utts.keys():
        epsilon_token = 1
        utt = utts[key]
        output = utt['output'][0]
        tokenid = output['tokenid']
        tokenid_list = tokenid.split(' ')
        for token in tokenid_list:
            if token in tokenid2num.keys():
                tokenid2num[token] += 1
            else:
                tokenid2num[token] = 1
            epsilon_token += 1
        epsilon_sum += epsilon_token
        token_sum += (2 * epsilon_token - 1)
    tokenid2num['0'] = epsilon_sum
    token_pro = np.zeros((len(tokenid2num),))
    for token, num in tokenid2num.items():
        index = int(token)
        token_pro[index] = num / token_sum
    np.save(os.path.join(dir, 'token_pro.npy'), token_pro)

