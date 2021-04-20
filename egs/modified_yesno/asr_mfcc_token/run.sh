#!/bin/bash

# Copyright 2017 Johns Hopkins University (Shinji Watanabe)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

. ./path.sh || exit 1;
. ./cmd.sh || exit 1;

# general configuration
backend=pytorch
stage=0      # start from -1 if you need to start from data download
stop_stage=100
ngpu=1         # number of gpus ("0" uses cpu, otherwise use gpu)
debugmode=1
dumpdir=dump   # directory to dump full features
N=0            # number of minibatches to be used (mainly for debugging). "0" uses all minibatches.
verbose=1      # verbose option
resume=        # Resume the training from snapshot

# feature configuration
do_delta=true

train_config=conf/train.yaml
decode_config=conf/decode.yaml

# decoding parameter
recog_model=model.loss.best # set a model to be used for decoding: 'model.acc.best' or 'model.loss.best'

# exp tag
tag="" # tag for managing experiments.
subtag=""
train_set=train_yyn
train_dev=dev_yyn
elayers=2
eunits=50
eprojs=50

. utils/parse_options.sh || exit 1;

set -euo pipefail

fbankdir=fbank
mfccdir=mfcc

# bpemode (unigram or bpe)
nbpe=4
bpemode=unigram

recog_set="train_yyn train_ynn train_3gram test_yyn test_ynn test_3gram test_sam_yyn test_sam_ynn test_sam_3gram test_sam_yyn_noise test_sam_ynn_noise test_sam_3gram_noise"

if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    ### Task dependent. You have to make data the following preparation part by yourself.
    ### But you can utilize Kaldi recipes in most cases
    echo "stage 0: Data preparation"
    data_dir=/disk/scratch3/zzhao/data/modified_yesno
    local/prepare_data.py --dir $data_dir
    local/prepare_sam_data.py --dir $data_dir
    local/prepare_sam_noise_data.py --dir $data_dir
    for x in train_yyn dev_yyn test_yyn train_ynn dev_ynn test_ynn train_3gram dev_3gram test_3gram; do
        sort data/$x/wav.scp > data/$x/wav.scp.sorted
        sort data/$x/text > data/$x/text.sorted
        sort data/$x/utt2spk > data/$x/utt2spk.sorted
        mv data/$x/wav.scp.sorted data/$x/wav.scp
        mv data/$x/text.sorted data/$x/text
        mv data/$x/utt2spk.sorted data/$x/utt2spk
        utils/utt2spk_to_spk2utt.pl <data/$x/utt2spk > data/$x/spk2utt
    done
    for x in test_sam_yyn test_sam_ynn test_sam_3gram test_sam_yyn_noise test_sam_ynn_noise test_sam_3gram_noise; do
        sort data/$x/wav.scp > data/$x/wav.scp.sorted
        sort data/$x/text > data/$x/text.sorted
        sort data/$x/utt2spk > data/$x/utt2spk.sorted
        mv data/$x/wav.scp.sorted data/$x/wav.scp
        mv data/$x/text.sorted data/$x/text
        mv data/$x/utt2spk.sorted data/$x/utt2spk
        utils/utt2spk_to_spk2utt.pl <data/$x/utt2spk > data/$x/spk2utt
    done
fi

feat_tr_dir=${dumpdir}/${train_set}/delta${do_delta}; mkdir -p ${feat_tr_dir}
feat_dt_dir=${dumpdir}/${train_dev}/delta${do_delta}; mkdir -p ${feat_dt_dir}

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    ### Task dependent. You have to design training and dev sets by yourself.
    ### But you can utilize Kaldi recipes in most cases
    echo "stage 1: Feature Generation"
     #Feature extraction
    #for x in train_yyn dev_yyn test_yyn train_ynn dev_ynn test_ynn train_3gram dev_3gram test_3gram; do
        #steps/make_mfcc.sh --nj 1 --write_utt2num_frames true data/${x} exp/make_mfcc/${x} ${mfccdir}
        #utils/fix_data_dir.sh data/${x}
        #steps/compute_cmvn_stats.sh data/${x} exp/make_mfcc/${x} ${mfccdir}
    #done
    #for x in test_sam_yyn test_sam_ynn test_sam_3gram test_sam_yyn_noise test_sam_ynn_noise test_sam_3gram_noise; do
        #steps/make_mfcc.sh --nj 1 --write_utt2num_frames true data/${x} exp/make_mfcc/${x} ${mfccdir}
        #utils/fix_data_dir.sh data/${x}
        #steps/compute_cmvn_stats.sh data/${x} exp/make_mfcc/${x} ${mfccdir}
    #done

    # compute global CMVN
    compute-cmvn-stats scp:data/${train_set}/feats.scp data/${train_set}/cmvn.ark

    # dump features
    dump.sh --cmd "$train_cmd" --nj 2 --do_delta ${do_delta} \
        data/${train_set}/feats.scp data/${train_set}/cmvn.ark exp/dump_feats/train ${feat_tr_dir}
    dump.sh --cmd "$train_cmd" --nj 2 --do_delta ${do_delta} \
        data/${train_dev}/feats.scp data/${train_set}/cmvn.ark exp/dump_feats/dev ${feat_dt_dir}
    for rtask in ${recog_set}; do
        feat_recog_dir=${dumpdir}/${rtask}/delta${do_delta}; mkdir -p ${feat_recog_dir}
        dump.sh --cmd "$train_cmd" --nj 2 --do_delta ${do_delta} \
            data/${rtask}/feats.scp data/${train_set}/cmvn.ark exp/dump_feats/recog/${rtask} \
            ${feat_recog_dir}
    done

fi

dict=data/lang_1char/${train_set}_units_word.txt
#dict=data/lang_char/${train_set}_${bpemode}${nbpe}_units.txt
#bpemodel=data/lang_char/${train_set}_${bpemode}${nbpe}
echo "dictionary: ${dict}"
if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    ### Task dependent. You have to check non-linguistic symbols used in the corpus.
    echo "stage 2: Dictionary and Json Data Preparation"
    mkdir -p data/lang_1char/
    #mkdir -p data/lang_char/
    #echo "<unk> 1" > ${dict} # <unk> must be 1, 0 will be used for "blank" in CTC
    echo "<unk> 1" > ${dict} # <unk> must be 1, 0 will be used for "blank" in CTC
    #cut -f 2- -d" " data/${train_set}/text > data/lang_char/input.txt
    #spm_train --input=data/lang_char/input.txt --vocab_size=${nbpe} --model_type=${bpemode} --model_prefix=${bpemodel} --input_sentence_size=100000000
    #spm_encode --model=${bpemodel}.model --output_format=piece < data/lang_char/input.txt | tr ' ' '\n' | sort | uniq | awk '{print $0 " " NR+1}' >> ${dict}
    #wc -l ${dict}

    text2token.py -s 1 -n 1 data/${train_set}/text | cut -f 2- -d" " | tr " " "\n" \
    | sort | uniq | grep -v -e '^\s*$' | awk '{print $0 " " NR+1}' >> ${dict}
    #text2vocabulary.py -s 2 data/${train_set}/text | cut -f 2- -d" " | tr " " "\n" \
    #| sort | uniq | grep -v -e '^\s*$' | awk '{print $0 " " NR+1}' >> ${dict}
    #text2vocabulary.py -s 2 data/${train_set}/text >> ${dict}
    wc -l ${dict}
    #data2json.sh --nj 1 --feat ${feat_sp_dir}/feats.scp --bpecode ${bpemodel}.model \
        #data/${train_sp} ${dict} > ${feat_sp_dir}/data_${bpemode}${nbpe}.json
    #data2json.sh --nj 1 --feat ${feat_dt_dir}/feats.scp --bpecode ${bpemodel}.model \
        #data/${train_dev} ${dict} > ${feat_dt_dir}/data_${bpemode}${nbpe}.json

    #for rtask in ${recog_set}; do
        #feat_recog_dir=${dumpdir}/${rtask}/delta${do_delta}
        #data2json.sh --nj 1 --feat ${feat_recog_dir}/feats.scp --bpecode ${bpemodel}.model \
            #data/${rtask} ${dict} > ${feat_recog_dir}/data_${bpemode}${nbpe}.json
    #done

    # make json labels
    data2json.sh --feat ${feat_tr_dir}/feats.scp\
         data/${train_set} ${dict} > ${feat_tr_dir}/data.json
    data2json.sh --feat ${feat_dt_dir}/feats.scp\
         data/${train_dev} ${dict} > ${feat_dt_dir}/data.json
    for rtask in ${recog_set}; do
        feat_recog_dir=${dumpdir}/${rtask}/delta${do_delta}
        data2json.sh --feat ${feat_recog_dir}/feats.scp\
            data/${rtask} ${dict} > ${feat_recog_dir}/data.json
    done
fi

if [ -z ${tag} ]; then
    expname=${train_set}_${backend}_$(basename ${train_config%.*})
    if ${do_delta}; then
        expname=${expname}_delta
    fi
    if [ ! -z ${subtag} ]; then
        expname=${expname}_${subtag}
    fi
else
    expname=${train_set}_${backend}_${tag}
fi
expdir=exp/${expname}
mkdir -p ${expdir}

if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "stage 3: Network Training"
    ${cuda_cmd} --gpu ${ngpu} ${expdir}/train.log \
        asr_train.py \
        --config ${train_config} \
        --elayers ${elayers} \
        --eunits ${eunits} \
        --eprojs ${eprojs} \
        --ngpu ${ngpu} \
        --backend ${backend} \
        --outdir ${expdir}/results \
        --tensorboard-dir tensorboard/${expname} \
        --debugmode ${debugmode} \
        --dict ${dict} \
        --debugdir ${expdir} \
        --minibatches ${N} \
        --verbose ${verbose} \
        --resume ${resume} \
        --train-json ${feat_tr_dir}/data.json \
        --valid-json ${feat_dt_dir}/data.json
fi

if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "stage 4: Decoding"
    nj=2

    pids=() # initialize pids
    for rtask in ${recog_set}; do
    (
        decode_dir=decode_${rtask}_$(basename ${decode_config%.*})
        feat_recog_dir=${dumpdir}/${rtask}/delta${do_delta}

        # split data
        splitjson.py --parts ${nj} ${feat_recog_dir}/data.json

        #### use CPU for decoding
        ngpu=0

        ${decode_cmd} JOB=1:${nj} ${expdir}/${decode_dir}/log/decode.JOB.log \
            asr_recog.py \
            --config ${decode_config} \
            --ngpu ${ngpu} \
            --backend ${backend} \
            --debugmode ${debugmode} \
            --verbose ${verbose} \
            --recog-json ${feat_recog_dir}/split${nj}utt/data.JOB.json \
            --result-label ${expdir}/${decode_dir}/data.JOB.json \
            --model ${expdir}/results/${recog_model}

        score_sclite.sh --wer true ${expdir}/${decode_dir} ${dict}

    ) &
    pids+=($!) # store background pids
    done
    i=0; for pid in "${pids[@]}"; do wait ${pid} || ((++i)); done
    [ ${i} -gt 0 ] && echo "$0: ${i} background jobs are failed." && false
    echo "Finished"
fi
