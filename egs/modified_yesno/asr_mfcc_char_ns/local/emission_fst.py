import os
import k2
import numpy as np
import torch
import argparse
import copy

parser = argparse.ArgumentParser(
    description='This programme can transform CTC posterior probabilities into emission FST.')

parser.add_argument('-t', '--train-data',
                    help='The directory of train data.', type=str, default='')
parser.add_argument('-d', '--data-directory',
                    help='lpz data directory', type=str, default='')
parser.add_argument('-n', '--normalise',
                    help='Whether or not normalise data by training data.', type=bool, default=True)
parser.add_argument('-w', '--word-file',
                    help='ESPnet word file', type=str, default='')

args = parser.parse_args()


def logaddlist(array):
    N = array.shape[0]
    ori = array[0, :]
    for i in range(1, array.shape[0]):
        ori = np.logaddexp(ori, array[i, :])
    ori = np.expand_dims(ori, axis=0)
    return ori - np.log(N)


def normalise(args):
    train_utts = []
    with open(os.path.join(args.train_data, 'wav.scp')) as f:
        for line in f:
            lc = line.strip().split()
            train_utts.append(lc[0])
    uttid2datafile = dict()
    with open(os.path.join(args.data_directory, 'lpz.scp')) as f:
        for line in f:
            lc = line.strip().split()
            uttid2datafile[lc[0]] = lc[1]
    lpz_means = []
    for utt in train_utts:
        datafile = uttid2datafile[utt]
        lpzdata = np.load(datafile)
        lpz_means.append(lpzdata)
    lpz_means = np.concatenate(lpz_means, axis=0)
    final_mean = logaddlist(lpz_means)
    np.save(os.path.join(args.data_directory, 'train_prior.npy'), final_mean)
    np.savetxt(os.path.join(args.data_directory, 'train_prior.txt'), final_mean)

    data_norm_dir = os.path.join(args.data_directory, 'data_norm')
    txtdata_norm_dir = os.path.join(args.data_directory, 'txtdata_norm')
    os.makedirs(data_norm_dir, exist_ok=True)
    os.makedirs(txtdata_norm_dir, exist_ok=True)

    with open(os.path.join(args.data_directory, 'lpz_norm.scp'), 'w') as f, open(os.path.join(args.data_directory, 'lpztxt_norm.scp'), 'w') as g:
        fc = ''
        gc = ''
        for utt in uttid2datafile.keys():
            datafile = uttid2datafile[utt]
            data = np.load(datafile)
            data_norm = data - np.repeat(final_mean, data.shape[0], axis=0)
            data_path = os.path.join(data_norm_dir, utt + '.npy')
            txtdata_path = os.path.join(txtdata_norm_dir, utt + '.txt')
            np.save(data_path, data_norm)
            np.savetxt(txtdata_path, data_norm)
            fc += '%s %s\n' % (utt, data_path)
            gc += '%s %s\n' % (utt, txtdata_path)
        f.write(fc)
        g.write(gc)


def symboletable(args):
    '''
    This programme read word_file and return a symboltable containing <eps>, <blank> and <eos>, which can be used as input symboltable for emission fst.
    '''
    with open(os.path.join(args.word_file)) as f:
        s = '<eps> 0\n<blank> 1\n'
        count = 2
        for line in f:
            lc = line.strip().split()
            s += '%s %d\n' % (lc[0], count)
            count += 1
        s += '<eos> %d' % (count)
    return s


def transform_utt(lpzdata):
    '''
    This programme transform one single lpzdata into emission fst.
    input:
    lpzdata: np.ndarray, with shape (n_frame, output_dim)
        output_char = ['<blank>', '<unk>', ..., '<eos>']
    # symboltable_str: str, symboltable 
        # '<eps> 0
        # a 1 
        # b 2 
        # ...
        # <eos> N'
    return:
    g: k2.Fsa, emission fsa
    aux_labels: torch.tensor, the corresponding aux_labels # we do so because k2 does not support read fst from txt directly.
    '''
    n_frame, output_dim = lpzdata.shape
    s = ''
    for frame in range(n_frame):
        for char in range(1, output_dim + 1):
            # begin with 1 because of 0 for epsilon
            s += '%d %d %d %d %.10f\n' % (frame, frame + 1,
                                          char, char, lpzdata[frame, char - 1])
    s += '%d %d -1 -1 0.0\n%d' % (n_frame, n_frame + 1, n_frame + 1)
    g = k2.Fsa.from_str(s, acceptor=False)
    return g


def transform(args):
    if args.normalise:
        normalise(args)
    symbols = symboletable(args)
    with open(os.path.join(args.data_directory, 'emission_symbols'), 'w') as f:
        f.write(symbols)
    lpzscp = os.path.join(args.data_directory, 'lpz.scp') if not args.normalise else os.path.join(
        args.data_directory, 'lpz_norm.scp')
    fstpath = os.path.join(args.data_directory, 'efst') if not args.normalise else os.path.join(
        args.data_directory, 'efst_norm')
    os.makedirs(fstpath, exist_ok=True)

    uttid2datafile = dict()
    with open(lpzscp) as f:
        for line in f:
            lc = line.strip().split()
            uttid2datafile[lc[0]] = lc[1]

    fst_scp = os.path.join(args.data_directory, 'efst.scp') if not args.normalise else os.path.join(
        args.data_directory, 'efst_norm.fst')
    with open(fst_scp, 'w') as f:
        fc = ''
        for uttid in uttid2datafile.keys():
            datafile = uttid2datafile[uttid]
            data = np.load(datafile)
            efst = transform_utt(data)
            efst_str = k2.to_str(efst)
            efst_file = os.path.join(fstpath, uttid)
            with open(efst_file, 'w') as g:
                g.write(efst_str)
            fc += '%s %s\n' % (uttid, efst_file)
        f.write(fc)


def lexicon_fst(args):
    '''
    This programme create lexicon.fst.pdf and lexicon.fst.txt based on args.word_file
    input:
    args: name_space
    return:
    lexicon: k2.Fsa, lexicon fst
    output:
    lexicon.fst.txt and lexicon.fst.pdf in args.data_directory

    By lexicon fst, we compress the repeated chars in emission fst. 
    '''
    symbols_str = symboletable(args)
    symbols_paris = symbols_str.split('\n')
    num_noneps = len(symbols_paris) - 1
    symbol2fst = [None]  # <eps> has no fst
    for i in range(1, num_noneps + 1):
        s = '''
        0 1 %d %d 0.0
        1 1 %d 0 0.0
        1 2 -1 -1 0.0
        2
        ''' % (i, i, i)
        g = k2.Fsa.from_str(s, acceptor=False)

        symbol2fst.append(g)
    fst_vec = k2.create_fsa_vec(symbol2fst[1:])
    fst_union = k2.union(fst_vec)
    lexicon = k2.closure(fst_union)
    lexicon.draw(os.path.join(args.data_directory, 'lexicon.fst.pdf'), title='lexicon')
    # lexicon.symbols = k2.SymbolTable.from_str(symbols_str)
    # lexicon.aux_symbols = k2.SymbolTable.from_str(symbols_str)
    with open(os.path.join(args.data_directory, 'lexicon.fst.txt'), 'w') as f:
        f.write(k2.to_str(lexicon))


def lexicon_fst_whole(args):
    '''
    This programme create lexicon.fst.pdf and lexicon.fst.txt based on args.word_file
    input:
    args: name_space
    return:
    lexicon: k2.Fsa, lexicon fst
    output:
    lexicon.fst.txt and lexicon.fst.pdf in args.data_directory

    By lexicon fst, we compress the repeated chars in emission fst. 
    '''
    symbols_str = symboletable(args)
    symbols_paris = symbols_str.split('\n')
    num_noneps = len(symbols_paris) - 1
    s = ''
    count = 1
    for i in range(1, num_noneps + 1):
        s += '''
0 %d %d %d 0.0
%d %d %d 0 0.0
%d %d -1 -1 0.0
%d 0 0 0 0.0''' % (
            i, i, i, i, i, i, i, num_noneps + 1, i)
    slines = s.strip().split('\n')
    def extract_first_index(line):
        line_content = line.strip().split()
        return int(line_content[0])
    slines = sorted(slines, key=lambda l: extract_first_index(l))
    s = '\n'.join(slines)

    s += '\n%d\n' % (num_noneps + 1)
    # s1 = '''
    # 0 1 1 1 0.0
    # 0 2 2 2 0.0
    # 0 3 3 3 0.0
    # 0 4 4 4 0.0
    # 0 5 5 5 0.0
    # 1 1 1 0 0.0
    # 1 6 -1 -1 0.0
    # 1 0 0 0 0.0
    # 2 2 2 0 0.0
    # 2 6 -1 -1 0.0
    # 2 0 0 0 0.0
    # 3 3 3 0 0.0
    # 3 6 -1 -1 0.0
    # 3 0 0 0 0.0
    # 4 4 4 0 0.0
    # 4 6 -1 -1 0.0
    # 4 0 0 0 0.0
    # 5 5 5 0 0.0
    # 5 6 -1 -1 0.0
    # 5 0 0 0 0.0
    # 6
    # '''
    with open('lex.txt', 'w') as f:
        f.write(s)
    g = k2.Fsa.from_str(s, acceptor=False)
    # g.symbols = k2.SymbolTable.from_str(symbols_str)
    # g.aux_symbols = k2.SymbolTable.from_str(symbols_str)
    g.draw(os.path.join(args.data_directory, 'lexicon.newfst.pdf'), title='lexicon')
    with open(os.path.join(args.data_directory, 'lexicon.newfst.txt'), 'w') as f:
        f.write(k2.to_str(g))


def gfst(args):
    '''
    This programme is for debugging only. 
    Usually, for different task, we need diffrent gfst.
    Imagine that we only have 
    '
    <eps> 0
    <blank> 1
    <unk> 2
    n 3 
    y 4
    <eos> 5
    '
    these 6 different symbols and try to generate yyn, ynn, and 3gram gfst.
    '''
    symbols = symboletable(args)
    yyn = '''
    0 1 0 0 0.0
    0 2 0 0 0.0
    0 3 0 0 0.0
    0 4 0 0 0.0
    0 5 0 0 0.0
    0 6 0 0 0.0
    1 2 4 4 0.0
    1 6 1 0 0.0
    1 7 5 5 0.0
    2 3 1 0 0.0
    2 7 5 5 0.0
    3 4 4 4 0.0
    3 7 5 5 0.0
    4 5 1 0 0.0
    4 1 3 3 0.0
    4 7 5 5 0.0
    5 1 3 3 0.0
    5 7 5 5 0.0
    6 2 4 4 0.0
    6 7 5 5 0.0
    7 8 -1 -1 0.0
    8
    '''
    yyn_fst = k2.Fsa.from_str(yyn, acceptor=False)
    # yyn_fst.symbols = k2.SymbolTable.from_str(symbols)
    # yyn_fst.aux_symbols = k2.SymbolTable.from_str(symbols)
    gfst_dir = os.path.join(args.data_directory, 'G')
    os.makedirs(gfst_dir, exist_ok=True)
    yyn_fst.draw(os.path.join(gfst_dir, 'yyn.pdf'), 'yyn')
    with open(os.path.join(gfst_dir, 'yyn.fst.txt'), 'w') as f:
        f.write(k2.to_str(yyn_fst))


if __name__ == '__main__':
    # print(args.normalise)
    # transform(args)
    # lexicon_fst(args)
    lexicon_fst_whole(args)
    gfst(args)
    # ar = np.load('/afs/inf.ed.ac.uk/user/s20/s2070789/Documents/asr_mfcc_char_lpz/data/ynn32.npy')
    # b = logaddlist(ar)
    # print(b)
    pass
