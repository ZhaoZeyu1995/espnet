#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser(
    description='This programme is for preparation of modified yesno.')

parser.add_argument('-d', '--dir', help='the path to the dataset.', type=str)
parser.add_argument('-s', '--snr', help='snr', type=int, default=16)
parser.add_argument('-n', '--num-audio',
                    help='number of noisy audio per original audio', type=int, default=10)

args = parser.parse_args()

if __name__ == '__main__':
    dir = args.dir
    for subdir in ['yyn', 'ynn']:
        samples = []
        with open(os.path.join(dir, 'trans_char', subdir + '.txt')) as f:
            for line in f:
                lc = line.strip().split()
                samples.append([lc[0], ' '.join(lc[1:])])
            samples = samples[30:]
        for sub_samples, sub_string in zip([samples],
                                           ['test']):
            data_dir = os.path.join('data', '%s_%s_SNR%s' %
                                    (sub_string, subdir, args.snr))
            os.makedirs(data_dir, exist_ok=True)
            wav_scp_content = []
            text_content = []
            utt2spk_content = []
            for sample in sub_samples:
                utt = sample[0]
                text = sample[1]
                for i in range(args.num_audio):
                    uttid = subdir + utt + '_%s' % args.snr + '_%d' % (i)
                    file_path = os.path.join(dir, subdir, 'SNR%d_%d' % (
                        args.snr, args.num_audio), utt + '_%d.wav' % (i))
                    wav_scp_content.append(uttid + ' ' + file_path)
                    text_content.append(uttid + ' ' + text)
                    utt2spk_content.append(uttid + ' ' + uttid)
            with open(os.path.join(data_dir, 'wav.scp'), 'w') as f:
                f.write('\n'.join(wav_scp_content) + '\n')
            with open(os.path.join(data_dir, 'text'), 'w') as f:
                f.write('\n'.join(text_content) + '\n')
            with open(os.path.join(data_dir, 'utt2spk'), 'w') as f:
                f.write('\n'.join(utt2spk_content) + '\n')
