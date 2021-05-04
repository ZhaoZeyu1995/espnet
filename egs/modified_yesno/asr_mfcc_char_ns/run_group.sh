#!/bin/bash

train_config=conf/train.yaml

for dataset in yyn ynn 3gram; do
    train_set=train_${dataset}
    train_dev=dev_${dataset}
    for elayers in 1 2 3; do
        for eunits in 50 60 70 80 90 100; do
            for random_seed in 1 2 3 4 5 6 7 8 9 10; do
                subtag=${elayers}_${eunits}_${random_seed}
                ./run.sh --stage 1 \
                    --train-config ${train_config} \
                    --subtag ${subtag} \
                    --train-set ${train_set} \
                    --train-dev ${train_dev} \
                    --elayers ${elayers} \
                    --eunits ${eunits} \
                    --eprojs ${eunits} \
                    --random-seed  ${random_seed}
            done 
        done
    done
done
