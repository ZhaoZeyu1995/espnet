#!/bin/bash

test_sets=""

for subset in test_yyn test_ynn; do
    for snr in 10 12 14 16 18; do
        test_sets="${test_sets} ${subset}_SNR${snr}"
    done
done
for train_set in train_yyn train_ynn; do
    for nlayer in 1 2 3; do
        for eunits in 50 60 70 80 90; do
            for random_seed in 1 3 5 7 9; do
                sum_wer=""
                expdir=exp/${train_set}_pytorch_train_delta_${nlayer}_${eunits}_${random_seed}
                exp_output_file="${expdir}/result.sum"
                [ -f ${exp_output_file} ] && rm ${exp_output_file}
                for test_set in ${test_sets}; do
                    result_file=${expdir}/decode_${test_set}_decode/result.txt
                    wer=`cat ${result_file} | grep -m 1 "Mean" | awk '{print $(NF-2)}'`
                    sum_wer="${sum_wer} ${wer}"
                done
                echo ${sum_wer} >> ${exp_output_file}
            done
        done
    done
done

#a=`cat exp/train_yyn_pytorch_train_nosub_delta_1_10_nosub/decode_test_yyn_decode/result.wrd.txt | grep -m 1 "Mean" | awk '{print $11}'`
#echo $a
