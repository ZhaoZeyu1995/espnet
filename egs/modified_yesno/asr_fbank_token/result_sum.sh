#!/bin/bash

output_file="asr_mfcc_spk.result"
for train_set in train_yyn train_ynn train_3gram; do
    for nlayer in 1 2 3; do
        for eunits in 10 20 30 40 50 60 70 80 90 100 110 120 130; do
            expdir=exp/${train_set}_pytorch_train_nosub_delta_${nlayer}_${eunits}_nosub
            sum_wer=""
            for test_set in test_yyn test_ynn test_3gram test_sam_yyn test_sam_ynn test_sam_3gram test_sam_yyn_noise test_sam_ynn_noise test_sam_3gram_noise; do
                result_file=${expdir}/decode_${test_set}_decode/result.wrd.txt
                wer=`cat ${result_file} | grep -m 1 "Mean" | awk '{print $11}'`
                sum_wer="${sum_wer} ${wer}"
            done
            sum_wer="${sum_wer}"
            echo ${sum_wer} >> ${output_file}
        done
    done
done

#a=`cat exp/train_yyn_pytorch_train_nosub_delta_1_10_nosub/decode_test_yyn_decode/result.wrd.txt | grep -m 1 "Mean" | awk '{print $11}'`
#echo $a
