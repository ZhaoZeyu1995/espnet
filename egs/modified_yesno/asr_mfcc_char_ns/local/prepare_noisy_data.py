#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser(
    description='This programme is for preparation of modified yesno.')

parser.add_argument('-d', '--dir', help='the path to the dataset.', type=str)

args = parser.parse_args()

if __name__ == '__main__':
    dir = args.dir
    for snr in ['10', '12', '14', '16', '18']:
        for subdir in ['yyn', 'ynn', '3gram']:

            samples = []
            with open(os.path.join(dir, 'trans_char', subdir + '.txt')) as f:
                for line in f:
                    lc = line.strip().split()
                    samples.append([lc[0], ' '.join(lc[1:])])
            for sub_samples, sub_string in zip([samples],
                                               ['test']):
                data_dir = os.path.join('data', '%s_%s_SNR%s' % (sub_string, subdir, snr))
                os.makedirs(data_dir, exist_ok=True)
                wav_scp_content = []
                text_content = []
                utt2spk_content = []
                for sample in sub_samples:
                    utt = sample[0]
                    text = sample[1]
                    uttid = subdir + utt + '_' + snr
                    file_path = os.path.join(dir, subdir, 'SNR%s' % (snr), utt + '.wav')
                    wav_scp_content.append(uttid + ' ' + file_path)
                    text_content.append(uttid + ' ' + text)
                    utt2spk_content.append(uttid + ' ' + uttid)
                with open(os.path.join(data_dir, 'wav.scp'), 'w') as f:
                    f.write('\n'.join(wav_scp_content) + '\n')
                with open(os.path.join(data_dir, 'text'), 'w') as f:
                    f.write('\n'.join(text_content) + '\n')
                with open(os.path.join(data_dir, 'utt2spk'), 'w') as f:
                    f.write('\n'.join(utt2spk_content) + '\n')
