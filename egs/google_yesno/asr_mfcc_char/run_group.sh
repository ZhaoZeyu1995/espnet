#!/bin/bash

train_config=conf/train.yaml

for dataset in yyn ynn 3gram; do
    train_set=train_${dataset}
    train_dev=dev_${dataset}
    for elayers in 1 2 3; do
        for eunits in 30 40 50 60 70 80 90 100 110 120; do
            subtag=${elayers}_${eunits}_nosub
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
