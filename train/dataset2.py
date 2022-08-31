#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 09:12:01 2019

@author: hcb
"""

import pywt, os
import torch
import numpy as np
import pandas as pd
from config2 import config
from torch.utils.data import Dataset
from sklearn.preprocessing import scale
from scipy import signal
from torch.utils.data import DataLoader



def resample(sig, target_point_num=None):
    '''
    对原始信号进行重采样
    :param sig: 原始信号
    :param target_point_num:目标型号点数
    :return: 重采样的信号
    '''
    sig = signal.resample(sig, target_point_num) if target_point_num else sig
    return sig

def scaling(X, sigma=0.1):
    #print(X.shape[0])
    #scalingFactor = np.random.normal(loc=1.0, scale=sigma, size=(1, X.shape[1]))
    scalingFactor = np.random.normal(loc=1.0, scale=sigma, size=(1, 1))
    myNoise = np.matmul(np.ones((X.shape[0], 1)), scalingFactor)
    return X * myNoise

def verflip(sig):
    '''
    信号竖直翻转
    :param sig:
    :return:
    '''
    return sig[::-1, :]

def shift(sig, interval=20):
    '''
    上下平移
    :param sig:
    :return:

    for col in range(sig.shape[1]):
        offset = np.random.choice(range(-interval, interval))
        sig[:, col] += offset
    '''
    offset = np.random.choice(range(-interval, interval))
    sig[:, 0] += offset
    return sig

def noise(sig, interval=20):
    a, b = sig.shape
    noise_ = (np.random.rand(a, b)-0.5) * interval
    return sig + noise_
    
def transform(sig, train=False):
    # 前置不可或缺的步骤
    # sig = resample(sig, config.target_point_num)
    # # 数据增强
    #if train:
       #if np.random.rand() > 0.2: sig = scaling(sig)
        # if np.random.randn() > 0.5: sig = verflip(sig)
       #if np.random.rand() > 0.2: sig = shift(sig)
       # if np.random.rand() > 0.2: sig = noise(sig)
    # 后置不可或缺的步骤
    sig = sig.transpose()
    sig = torch.tensor(sig.copy(), dtype=torch.float)
    return sig


class ECGDataset(Dataset):
    """
    A generic data loader where the samples are arranged in this way:
    dd = {'train': train, 'val': val, "idx2name": idx2name, 'file2idx': file2idx}
    """

    def     __init__(self, data_path, train=True, transfer=False, transform=False):
        super(ECGDataset, self).__init__()
        #config.train_data = config.train_data + str(args.fold) + '.pth'
        dd = torch.load(config.train_data)
        #dd = torch.load(config.train_data+'1'+'.pth')
        self.train = train
        self.data = dd['train'] if train else dd['val']
        self.idx2name = dd['idx2name']
        self.file2idx = dd['file2idx']
        self.wc = []
        self.transfer = transfer
        self.transform = transform
#        for i in range(len(dd['wc'])):
#            if dd['wc'][i] < 10:
#                self.wc.append(3)
#            elif dd['wc'][i] < 100:
#                self.wc.append(2.5)
#            elif dd['wc'][i] < 500:
#                self.wc.append(2)
            
        self.wc = 2. / np.log(dd['wc'] + 1.1)
        # self.wc = 1. / np.log(dd['wc'] * 2 + 1)

    def __getitem__(self, index):
        fid = self.data[index]
        if self.transfer:
            file_path = fid
        else:
            file_path = os.path.join(config.train_dir, fid)
        df = pd.read_csv(file_path, sep=' ', engine='python')
        # df['III'] = df['II'] - df['I']
        # df['aVR'] = -(df['I'] + df['II']) / 2
        # df['aVL'] = df['I'] - df['II'] / 2
        # df['aVF'] = df['II'] - df['I'] / 2
        df = df.iloc[:,0]
        df = df.values
        x = transform(df, self.transform)
        #x = x.unsqueeze(0)
        target = np.zeros(config.num_classes)
        target[self.file2idx[fid]] = 1
        target = torch.tensor(target, dtype=torch.float32)
        return x, target

    def __len__(self):
        return len(self.data)


class ECGDataset_test(Dataset):

    def __init__(self, data_path_all):
        super(ECGDataset_test, self).__init__()
        self.data = data_path_all
        self.train = False

    def __getitem__(self, index):
        fid = self.data[index]
        file_path = os.path.join(fid)
        df = pd.read_csv(file_path, sep=' ', engine='python')
        df['III'] = df['II'] - df['I']
        df['aVR'] = -(df['I'] + df['II']) / 2
        df['aVL'] = df['I'] - df['II'] / 2
        df['aVF'] = df['II'] - df['I'] / 2
        df = df.values
        x = transform(df, self.train)
        target = 0
        target = torch.tensor(target, dtype=torch.float32)
        return x, target

    def __len__(self):
        return len(self.data)
    

def my_collate_fn(batch):
    data, label = zip(*batch)
    new_data = []
    new_label = []
    batch_size = len(label)
    len_ = int(3000 + np.random.rand() * 2000)
    #print(data)
    #print(label)
    #print(np.size((np.array(data))))
    #print(np.size((np.array(label))))
    for i in range(batch_size):
        start = int(np.random.rand() * (config.target_point_num - len_))
        #print(data[i])
        #print(np.shape((np.array(data[i]))))
        #print(label[i])
        #print(np.shape((np.array(label[i]))))
        #tmp_data = data[i].transpose(0, 1)
        tmp_data = data[i]
        #print(tmp_data.size())
        if i == 0:
            #new_data = (tmp_data[start:(start+len_)].transpose(0, 1)).unsqueeze(0)
            new_data = (tmp_data[start:(start + len_)]).unsqueeze(0)
            new_label = label[i].unsqueeze(0)
        else:
            #new_data = torch.cat((new_data, (tmp_data[start:(start+len_)].transpose(0, 1)).unsqueeze(0)), 0)
            new_data = torch.cat((new_data, (tmp_data[start:(start + len_)]).unsqueeze(0)), 0)
            new_label = torch.cat((new_label, label[i].unsqueeze(0)), 0)
    new_data = new_data.unsqueeze(0)
    new_data = new_data.transpose(1,0)
    #print(new_data.size())
    return new_data, new_label


if __name__ == '__main__':
    #train_dataset = ECGDataset(data_path=config.train_data, train=True, transform=True)
    #train_dataloader = DataLoader(train_dataset, collate_fn=my_collate_fn,
#                                  batch_size=64, shuffle=True, num_workers=3)
    #print("train_datasize", len(train_dataset))
    d = ECGDataset(config.train_data)
    print(d[0])
