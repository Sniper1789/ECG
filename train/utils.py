# -*- coding: utf-8 -*-
'''
@time: 2019/9/12 15:16

@ author: javis
'''
import torch
import numpy as np
import time, os
from sklearn.metrics import f1_score
from torch import nn


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

#计算F1score
def calc_f1(y_true, y_pre, threshold=0.5):
    y_true = y_true.view(-1).cpu().detach().numpy().astype(np.int)
    y_pre = y_pre.view(-1).cpu().detach().numpy() > threshold
#    y_pre = y_pre.cpu().detach().numpy() > threshold
#    for i in [0, 2, 6, 7, 8, 14, 15, 16, 19, 21, 23, 25, 32, 33]:
#	    y_pre[:, i] = np.zeros(len(y_pre))
#    y_pre = y_pre.reshape(-1)
    return f1_score(y_true, y_pre)


def calc_acc_f1(y_true, y_pred, threshold=0.5):
    y_true = y_true.cpu().detach().numpy().astype(np.int)
    y_pred = y_pred.cpu().detach().numpy() > threshold
    true_positives = np.sum(np.round(np.clip(y_true * y_pred, 0, 1)), axis=0)
    real_positives = np.sum(np.round(np.clip(y_true, 0, 1)), axis=0)
    predicted_positives = np.sum(np.round(np.clip(y_pred, 0, 1)), axis=0)
    acc = np.sum(y_true == y_pred, axis=0) / len(y_true)
    return acc, true_positives, real_positives, predicted_positives


#打印时间
def print_time_cost(since):
    time_elapsed = time.time() - since
    return '{:.0f}m{:.0f}s\n'.format(time_elapsed // 60, time_elapsed % 60)


# 调整学习率
def adjust_learning_rate(optimizer, lr):
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr

#多标签使用类别权重
class WeightedMultilabel(nn.Module):
    def __init__(self, weights: torch.Tensor):
        super(WeightedMultilabel, self).__init__()
        self.cerition = nn.BCEWithLogitsLoss()
        self.weights = weights
    def forward(self, outputs, targets):
        outputs[outputs > 13] = 13
        outputs[outputs < -13] = -13
        loss = self.cerition(outputs, targets)
        return (loss * self.weights).mean()


class My_loss(nn.Module):
    def __init__(self, weights: torch.Tensor):
        super().__init__()
#        self.weights = weights
        self.weights = torch.tensor(np.ones(55), dtype=torch.float).to(device)
        for i in list(range(16,55)):
            self.weights[i] = 0
    def forward(self, y_pred, y_true):
        y_pred[y_pred > 13] = 13
        y_pred[y_pred < -13] = -13
        y_pred = torch.sigmoid(y_pred)
        loss = torch.mean(1.5 * y_true * torch.log(y_pred) + 1 * (1 - y_true) * torch.log(1 - y_pred), 0)
        # print(0.9 * y_true * torch.log(y_pred + 0.000001))
        return -(loss * self.weights).mean()


class WeightedMultilabel2(nn.Module):
    def __init__(self, weights: torch.Tensor):
        super(WeightedMultilabel2, self).__init__()
        self.cerition = nn.BCEWithLogitsLoss()
        self.weights = weights
    def forward(self, outputs, targets):
        outputs[outputs > 13] = 13
        outputs[outputs < -13] = -13
        #print(targets.size())
        loss = self.cerition(outputs, targets)
        return (loss * self.weights).mean()

# a = torch.tensor([[1, 2], [2, 3]], dtype=torch.float32)
# b = torch.tensor([[0, 1], [2, 3]], dtype=torch.float32)
#
# criterion = My_loss(torch.tensor([0.1,0.2]))
# loss = criterion(a, b)
# print(loss)