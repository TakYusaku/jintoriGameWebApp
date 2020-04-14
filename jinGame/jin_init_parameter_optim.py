import datetime
import math
import sys
import pandas as pd
import pickle
import random
import numpy as np
import mimetypes
import json
import copy
import os

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from jin_NN import *

def load_csv(environ_df, features_list, before_features_list, category_list, states_num):
    # To be encoded as one-hot vector
    day_of_the_week_idx = features_list.index('dayOfTheWeek')
    day_of_the_week_len = 7

    #indexメソッド 引数に調べたい値を指定すると0始まりのインデックスが取得
    category_id_idx = features_list.index('categoryId')
    category_id_len = len(category_list)
    #day_of_the_week と category_idがonehotに変換される
    onehot_idx_list = [day_of_the_week_idx, category_id_idx]
    onehot_len_list = [day_of_the_week_len, category_id_len]
    
    # csvファイルのデータからfeature_listのところだけ抜き出す
    df_next = environ_df[features_list]
    df_before = environ_df[before_features_list]

    # csvファイル(numpy_array)からtorchの型に変更する
    df_next = torch.from_numpy(df_next.values).float()
    # df_next の onehot_idx_list に当たるデータをonehot_len_listの長さでonehotベクトル化する
    df_next = encode_onehot(df_next, onehot_idx_list, onehot_len_list)
    df_next = normalize_mask(df_next, onehot_idx_list, onehot_len_list)

    df_before = torch.from_numpy(df_before.values).float()
    df_before = encode_onehot(df_before, onehot_idx_list, onehot_len_list)
    df_before = normalize_mask(df_before, onehot_idx_list, onehot_len_list)
    
    data = torch.cat(
        (df_before, df_next),
        dim=0
    )
    #to GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = data.to(device)

    return data

def param_init_model(data, k_division, states_num, on_eps_zero, ite = 20, epoch = 100):
    
    if on_eps_zero:
        model = DQN_epsZero(states_num, k_division)
    else:
        model = DQN(states_num, k_division)
    
    #to GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)
    label = 10*torch.ones((data.size()[0], k_division))
    #to GPU
    label = label.to(device)
    criterion = nn.MSELoss()
    l=[]
    for _ in range(epoch):
        tmploss=0
        for i in range(ite):
            optimizer.zero_grad()
            out = model(data)
            loss = criterion(out, label)
            loss.backward()
            for param in model.parameters():
                #勾配の値を直接変更する
                #https://pytorch.org/docs/master/torch.html#torch.clamp
                param.grad.data.clamp_(-1, 1)
            optimizer.step()
            tmploss+=loss.item()/ite
        l.append(loss.item())
    l = np.array(l)
    
    return model
