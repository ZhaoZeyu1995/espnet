import numpy as np

for train_set in ['train_yyn']:
    for nlayer in [1, 2, 3]:
        for eunits in [50, 60, 70, 80, 90, 100]:
            average_list = []
            for random_seed in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                exp_dir = 'exp/%s_pytorch_train_delta_%d_%d_%d' % (train_set,
                                                                   nlayer, eunits, random_seed)
                result = np.loadtxt(exp_dir + '/result.sum')
                result = np.expand_dims(result, axis=0)
                average_list.append(result)
            aver = np.concatenate(average_list, axis=0)
            aver = np.mean(aver, axis=0, keepdims=False)
            np.savetxt('exp/%s_pytorch_train_delta_%d_%d.txt' % (train_set, nlayer, eunits), aver)

