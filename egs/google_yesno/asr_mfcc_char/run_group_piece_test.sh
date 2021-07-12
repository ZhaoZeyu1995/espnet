#!/bin/bash

train_config=conf/train.yaml

for dataset in 3gram; do
    train_set=train_${dataset}
    train_dev=test_${dataset}
    for elayers in 1 2 3; do
        for eunits in 10 20 30 40 50 60 70 80 90 100 110 120 130; do
            subtag=${elayers}_${eunits}_nosub_test
            ./run.sh --stage 1 \
                --train-config ${train_config} \
                --subtag ${subtag} \
                --train-set ${train_set} \
                --train-dev ${train_dev} \
                --elayers ${elayers} \
                --eunits ${eunits} \
                --eprojs ${eunits}
        done
    done
done
