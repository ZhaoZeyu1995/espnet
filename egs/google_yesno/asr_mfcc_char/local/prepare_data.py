#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser(
    description='This programme is for preparation of modified yesno.')

parser.add_argument('-d', '--dir', help='the path to the dataset.', type=str)

args = parser.parse_args()

if __name__ == '__main__':
    dir = args.dir
    for subdir in ['yyn', 'ynn']:

        train_samples = []
        with open(os.path.join(dir, 'train_' + subdir, 'trans_char')) as f:
            for line in f:
                lc = line.strip().split()
                train_samples.append([lc[0], ' '.join(lc[1:])])
        dev_samples = []
        with open(os.path.join(dir, 'dev_' + subdir, 'trans_char')) as f:
            for line in f:
                lc = line.strip().split()
                dev_samples.append([lc[0], ' '.join(lc[1:])])
        test_samples = []
        with open(os.path.join(dir, 'test_' + subdir, 'trans_char')) as f:
            for line in f:
                lc = line.strip().split()
                test_samples.append([lc[0], ' '.join(lc[1:])])
        for sub_samples, sub_string in zip([train_samples, dev_samples, test_samples],
                                           ['train', 'dev', 'test']):
            data_dir = os.path.join('data', '%s_%s' % (sub_string, subdir))
            os.makedirs(data_dir, exist_ok=True)
            wav_scp_content = []
            text_content = []
            utt2spk_content = []
            for sample in sub_samples:
                utt = sample[0]
                text = sample[1]
                uttid = subdir + utt
                file_path = os.path.join(dir, sub_string + '_' + subdir, utt + '.wav')
                wav_scp_content.append(
                    uttid + ' ' + 'cat %s | sox - -r 8000 -t wav - |' % (file_path))
                text_content.append(uttid + ' ' + text)
                utt2spk_content.append(uttid + ' ' + uttid)
            with open(os.path.join(data_dir, 'wav.scp'), 'w') as f:
                f.write('\n'.join(wav_scp_content) + '\n')
            with open(os.path.join(data_dir, 'text'), 'w') as f:
                f.write('\n'.join(text_content) + '\n')
            with open(os.path.join(data_dir, 'utt2spk'), 'w') as f:
                f.write('\n'.join(utt2spk_content) + '\n')
