# -*- coding: utf-8 -*-

import os


class Config:
    # for data_process.py
    #root = r'D:\ECG'
    # root = r'../'

    #sub_file = '/tcdata/hf_round2_train.txt'
    sub_file = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_subA.txt'
    #sub_file = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_label.txt'
    #feature = '_test.csv'
    #arrythmia_file = 'hf_round2_arrythmia.txt'
    #file_path = '/tcdata/hf_round2_train'
    feature = '_test.csv'
    arrythmia_file = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_arrythmia.txt'
    file_path = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_testA\testA'
    #file_path = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_train\train'
    #label的类别数
    num_classes = 55#34
    #最大训练多少个epoch
    sub_dir = '../../'
    result_path = os.path.join(sub_dir, 'result.txt')
    save_name = 'train_ml.csv'
    save_name2 = 'test_ml.csv'

config = Config()
