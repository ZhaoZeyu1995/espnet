import numpy as np

for train_set in ['train_yyn', 'train_ynn']:
    all_res = []
    for nlayer in [1, 2, 3]:
        for eunits in [50, 60, 70, 80, 90]:
            average_list = []
            for random_seed in [1, 3, 5, 7, 9]:
                exp_dir = 'exp/%s_pytorch_train_delta_%d_%d_%d' % (train_set,
                                                                   nlayer, eunits, random_seed)
                result = np.loadtxt(exp_dir + '/result.sum')
                result = np.expand_dims(result, axis=0)
                average_list.append(result)
            aver = np.concatenate(average_list, axis=0)
            aver = np.mean(aver, axis=0, keepdims=True)
            all_res.append(aver)
    all_res = np.concatenate(all_res, axis=0)
    np.savetxt('exp/%s_pytorch_train_delta.txt' %
               (train_set), all_res, fmt='%.2f')
