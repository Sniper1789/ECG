#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 14:43:29 2019

@author: hcb
"""

import pandas as pd
import os
import numpy as np
from sklearn import metrics
import pickle
import tqdm
import lightgbm as lgb
import warnings
import catboost as cat
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')


def score_acc2(pred, data_vali):
    real = data_vali.get_label()
    p = np.round(pred)
    # fpr, tpr, thresholds = metrics.roc_curve(real, pred, pos_label=1)
    return 'auc', metrics.accuracy_score(real, p), True


def fscore(y_true, y_pred, threshold):
    for i in range(55):
        y_pred[:,i] = (y_pred[:,i] > threshold[i])
    # print(y_pred)
    pred_true_sample = np.sum(np.round(np.clip(y_true * y_pred, 0, 1)), axis=0)
    pred_sampe = np.sum(np.round(y_pred), axis=0)
    true_sample = np.sum(np.round(y_true), axis=0)
    p = np.sum(pred_true_sample) / (np.sum(pred_sampe) + 0.00001)
    r = np.sum(pred_true_sample) / (np.sum(true_sample) + 0.00001)
    f = 2 * p * r / (p + r + 0.00001)
    return np.mean(f), pred_true_sample, pred_sampe, true_sample


def read_list(labelfile, label_num):
    filenameslist = []
    filelabelslist = []
    file_age = []
    file_sex = []

    for i in tqdm.tqdm(range(len(labelfile))):
        col = [tmp for tmp in labelfile.columns if tmp not in ['File_name', 'age', 'sex']]
        label = [0 for i in range(label_num)]
        for tmp in col:
            if pd.isnull(labelfile[tmp][i]) == False:
                label[int(labelfile[tmp][i])] = 1
        filenameslist.append(labelfile['File_name'][i])
        if pd.isnull(labelfile['age'][i]) == False:
            file_age.append(labelfile['age'][i])
        else:
            file_age.append(0)
        if pd.isnull(labelfile['sex'][i]) == False:
            file_sex.append(labelfile['sex'][i])
        else:
            file_sex.append(3)

        filelabelslist.append(label)

    return filenameslist, filelabelslist, file_age, file_sex


use_age_sex = 1
is_test = 0
get_leaf = True
#train_data_path = 'E:\\code\\合肥心电\\hf_round1_train\\train'
#test_path = 'E:\\code\\合肥心电\\hf_round1_testA\\testA'
#label_file = 'hf_round2_train.txt'
#sub_file = 'E:\\code\\合肥心电\\hf_round1_subA.txt'
#arrythmia = 'hf_round2_arrythmia.txt'
label_file = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_label.txt'
arrythmia = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_arrythmia.txt'
base_path1 = 'DL_feature'
base_path3 = 'prob'
base_path2 = 'idx'
label_num = 55
add_ml_feature = 1

col = ['File_name', 'age', 'sex', 0, 1, 2, 3, 4, 5]
label = pd.read_csv(label_file, delimiter='\t', header=None, names=col) # delimiter='\t'
# label.columns = ['File_name', 'age', 'sex', 0, 1, 2, 3, 4, 5, 6, 7, 8]
# label.drop([8], axis=1, inplace=True)
label_map = pd.read_csv(arrythmia, delimiter='\t', header=None, encoding='utf-8', engine='python')
# label_map.drop([1, 2, 3], axis=1, inplace=True)
label_dict = dict(zip(label_map[0].unique(),range(label_map[0].nunique())))
label_map['code'] = label_map[0].map(label_dict)
sex_map = {'FEMALE': 0, 'MALE':1}
label['sex'] = label['sex'].map(sex_map)
for i in range(6):
    label[str(i)+'_code'] = label[i].map(label_dict)
label.drop([0, 1, 2, 3, 4, 5], axis=1, inplace=True)
filenameslist, filelabelslist, file_age, file_sex = read_list(label, label_num)
filelabelslist = np.array(filelabelslist)
label = label.rename(columns={'File_name': 'filename'})

result = []
ff = []

oof = np.zeros((len(filelabelslist), label_num))

if add_ml_feature == 1:
    data2 = pd.read_csv('train_ml.csv', header=0, engine='python')


model_name = 'lgb'
mask_value = -9999
feature_len = 512

# my_file = pd.read_csv('mylabel.csv')
# my_file = list(my_file['File_name'])

for i in range(5):
#    if i in [0]:
#        continue
#     read data
    print('-----------' + str(i) + '---------------')
    data = data2.copy()
    data = data.merge(label[['filename', 'age', 'sex']], 'left', on='filename')

    col = [str(i) for i in range(167)] + ['age', 'sex']
#    col = col1 + ['age', 'sex']
    #trn_idx = np.load(os.path.join(base_path2,  'train'+str(i)+'.npy'))
    #val_idx = np.load(os.path.join(base_path2, 'val'+str(i)+'.npy'))

    #trn_idx = data['filename'].isin(trn_idx)
    #val_idx = data['filename'].isin(val_idx)

    # read idx

    val_idx = [ii for ii in range(i, len(filenameslist), 5)]
    trn_idx = [ii for ii in range(len(filenameslist)) if ii not in val_idx]
    data = data[col].values
    #print(data.shape)
    # for ii in trn_idx.copy():
    #     if filenameslist[ii] not in my_file:
    #         trn_idx.remove(ii)
    # for ii in val_idx.copy():
    #     if filenameslist[ii] not in my_file:
    #         val_idx.remove(ii)

    trn_data = data[trn_idx]
    val_data = data[val_idx]
    print(val_data.shape, trn_data.shape)
    trn_label = filelabelslist[trn_idx]
    val_label = filelabelslist[val_idx]
    pred = np.zeros(val_label.shape)
    tmp_pred = np.zeros(filelabelslist.shape)
    tmp_result = []
    
    for j in range(label_num):
#        col = [str(i)] + ['age', 'sex']
#        trn_data = data[col][trn_idx].values
#        val_data = data[col][val_idx].values
        # if j < 5:
        #     continue
        print('folds: %d, label: %d' % (i, j))
        if use_age_sex == 0:
            save_base_path = os.path.join('model_ml', str(i))
        else:
            save_base_path = os.path.join('model_ml', str(i))
        if os.path.exists(save_base_path) == False:
            os.mkdir(save_base_path)

        params = {
            'learning_rate': 0.05,
            'boosting_type': 'gbdt',
            'objective': 'binary',
            'metric': 'binary_logloss',
#            'metric': 'auc',
            'num_leaves': 31,
            'feature_fraction': 0.95,
            'bagging_fraction': 0.95,
            'bagging_freq': 5,
            # 'is_unbalance': True,
            'seed': 1,
            'bagging_seed': 1,
            'feature_fraction_seed': 7,
            #'min_data_in_leaf': 5,
            'min_data_in_leaf': 5,
            'nthread': -1,
            'verbose': -1
        }
#
        dtrain = lgb.Dataset(trn_data, label=trn_label[:, j])
        dvalid = lgb.Dataset(val_data, label=val_label[:, j])
        save_path = os.path.join(save_base_path, 'model_' + model_name + str(j) + '.pickle')
        if is_test == 0:
            if model_name == 'lgb':
                clf = lgb.train(
                    params=params,
                    train_set=dtrain,
                    num_boost_round=10000,
                    valid_sets=[dvalid],
                    early_stopping_rounds=100,
                    verbose_eval=300,
                    # feval=score_acc2
                )
            if model_name == 'rf':
                from sklearn.ensemble import RandomForestClassifier
                clf = RandomForestClassifier(n_estimators=100, max_depth=11)
                trn_data[np.isnan(trn_data)] = mask_value
                clf.fit(trn_data, trn_label[:, j])
            if model_name == 'cat':
                clf = cat.CatBoostClassifier(random_state=2019, boosting_type='Plain')
                trn_data[np.isnan(trn_data)] = mask_value
                clf.fit(trn_data, trn_label[:, j], eval_set=(val_data, val_label[:, j]), verbose=1000)
        else:
            with open(save_path, 'rb+') as f:
                clf = pickle.load(f)
#        break
        if model_name == 'lgb':
            oof[val_idx, j] = clf.predict(val_data, num_iteration=clf.best_iteration)
        elif model_name == 'rf':
            val_data[np.isnan(val_data)] = mask_value
            oof[val_idx, j] = clf.predict(val_data)
        elif model_name == 'cat':
            val_data[np.isnan(val_data)] = mask_value
            oof[val_idx, j] = clf.predict(val_data)
        pred[:, j] = np.round(oof[val_idx, j])
        
        if get_leaf:
            tmp_pred = clf.predict(data, pred_leaf=True)
            leaf_path = os.path.join('model_ml', 'path'+str(i))
            if os.path.exists(leaf_path) == False:
                os.mkdir(leaf_path)
            leaf_path = os.path.join(leaf_path, str(j)+'.csv')
            df = pd.DataFrame(tmp_pred)
            df['filename'] = data2['filename']
            df.to_csv(leaf_path, index=None)
      
        if is_test == 0:
            with open(save_path, 'wb') as f:
                pickle.dump(clf, f)
    threshold = np.ones(55) * 0.5
    f1, pred_true_sample, pred_sampe, true_sample = fscore(val_label, oof[val_idx], threshold)
    print(f1)
    ff.append(f1)
    result.append(tmp_result)
    
#    if get_leaf:
#        df = pd.DataFrame(tmp_pred)
#        df['filename'] = data2['filename']
#        df.to_csv('ML_feature/' + str(i) + '_test.csv', index=None)

print(np.mean(ff))

f1, pred_true_sample, pred_sampe, true_sample = fscore(filelabelslist, oof, threshold)
df = pd.DataFrame(true_sample)
df = pd.concat((df, pd.DataFrame(pred_true_sample)), axis=1)
df = pd.concat((df, pd.DataFrame(pred_sampe)), axis=1)
df.columns = ['P', 'TP', 'PP']
df['FP'] = df['PP'] - df['TP']
df['RN'] = len(filelabelslist) -df['P']
df['TN'] = df['RN'] - df['FP']
df['FN'] = df['P'] - df['TP']
df.to_csv('result'+'.csv')
print(f1)