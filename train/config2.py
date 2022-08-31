#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:25:31 2019

@author: hcb
"""
import os


class Config:
    # for data_process.py
    #root = r'D:\ECG'
    root = r'D:\hefei\hefei_ecg-master otto\data'
    root2 = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_train'
    root3 = r'D:\hefei\hefei_ecg-master otto\data\hf_round1_testA'
    #root = r'/tcdata'
#    train_dir = os.path.join(root, 'hf_round1_train')
    train_dir = os.path.join(root2, 'train')
    test_dir = os.path.join(root3, 'testA')
    train_label = os.path.join(root, 'hf_round1_label.txt')
    test_label = os.path.join(root, 'hf_round1_subA.txt')
    arrythmia = os.path.join(root, 'hf_round1_arrythmia.txt')
    train_data = 'path/train'
    
    train_dir_round1_train = os.path.join(root2, 'train')
    train_dir_round1_test = os.path.join(root3, 'testA')

    # for train
    #训练的模型名称
    model_name = 'myecgnet'
    #在第几个epoch进行到下一个state,调整lr
#    stage_epoch = [5, 10, 15, 20]
    stage_epoch = [5, 10, 15, 20, 25]
    #训练时的batch大小
    batch_size = 64
    #label的类别数
    num_classes = 55#34
    #最大训练多少个epoch
    max_epoch = 5
    #目标的采样长度
    target_point_num = 5000
    #保存模型的文件夹
    ckpt = 'ckpt'
    #保存提交文件的文件夹
    sub_dir = 'submit'
    #初始的学习率
    lr = 1e-4 * 2
    #保存模型当前epoch的权重
    current_w = 'current_w.pth'
    #保存最佳的权重
    best_w = 'best_w.pth'
    # 学习率衰减 lr/=lr_decay
    lr_decay = 1.32

    #for test
    temp_dir = os.path.join(root, 'temp')


config = Config()
