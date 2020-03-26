from jin_consts, jin_init_parameter_optim, jin_parameter, jin_replayMemory import *
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
import deque
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from jinGame import jinGAME
from jin_replayMemory import *
from jin_util import *
from jin_consts import *
from jin_NN import *

def get_dim_list(li): # 2次元配列(list)のshapeを取得
    return [len(li),len([len(v) for v in li])]

class jinGame_DQNAgent():
    # 何か初期化がいるなら追加する
    def __init__(self,k_division=17, states_number=18, eps_start=0.99, eps_end=0.1, eps_decay=100,gamma=0.9, target_update=7):
        self.k_division = k_division
        self.states_number = states_number
        self.actions_number = k_division
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.gamma = gamma
        self.target_update = target_update
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #以下の変数はrun agentのタイミングで初期化する。これらは商品の数によって決まる。
        self.numberOfProducts = 0
        self.batch_size = 0
        self.memory_length = 0
        self.samplingCount = 0
        self.averageLoss = -1

        self.action_history = deque() # 行った行動を保存しておく
        self.agent_history = [[],[],[]] # [[#loss_median], [# target_name], [# policy_name]]

    #初期化
    def _init_agent(self, flg=False):
        if not flg: # 学習のとき
            self.policy_net = DQN(self.states_number, self.actions_number).to(self.device)
            self.target_net = DQN(self.states_number, self.actions_number).to(self.device)
            self.target_net.eval()
            self.optimizer = optim.RMSprop(self.policy_net.parameters(),lr=1e-4)
            self.replay_memory = ReplayMemory(self.memory_length)
        else: # evaluationのとき
            self.policy_net_a = DQN(self.states_number, self.actions_number).to(self.device)
            self.target_net_a = DQN(self.states_number, self.actions_number).to(self.device)
            self.policy_net_e = DQN(self.states_number, self.actions_number).to(self.device)
            self.target_net_e = DQN(self.states_number, self.actions_number).to(self.device)

    def _load_agent(self,file_name=None,flg=False): # fn_agent = {"policy": [name], "target": [name] }
        if not flg: # 学習の際
            if file_name is None:
                self.policy_net.load_state_dict(torch.load(PARAMETER_DIRECTORY_NAME + IMPORT_POLICY_FILE_NAME))
                self.target_net.load_state_dict(torch.load(PARAMETER_DIRECTORY_NAME + IMPORT_TARGET_FILE_NAME))
            else:
                self.policy_net.load_state_dict(torch.load(file_name['policy']))
                self.target_net.load_state_dict(torch.load(file_name['target']))            
        else: # evaluationのとき
                self.policy_net_a.load_state_dict(torch.load(file_name[0]['policy']))
                self.target_net_a.load_state_dict(torch.load(file_name[0]['target']))   
                self.policy_net_e.load_state_dict(torch.load(file_name[1]['policy']))
                self.target_net_e.load_state_dict(torch.load(file_name[1]['target']))   
    '''
    def _select_row_by_userID(self, userID):
        # replay_memoryのデータを取得
        # replay_memory_memory = :replay_memory_memory, steps_done = :steps_done
        # result = db_agent.get_item(Key={'k_division': k_division, 'item_id': item_id})
        # 上のやつを参考にデータを取得
        row_file_name = REPLAYMEMORY_DIRECTORY_NAME + IMPORT_REPLAYMEMORY_FILE_NAME
        try:
            row = result
        except:
            print("not found memory by userID")
            row = None
        finally:
            return row
    '''
    #replay_memoryにはmemory_lengthだけ格納することができる。その中から一回だけ、batch_size分だけ取得して学習する。
    def _optimize_model(self):
        #replay_memoryにbatch_size分だけ入っていない時は中止する
        if len(self.replay_memory) < self.batch_size:
            return
        sampled_data = self.replay_memory.sample(self.batch_size)
        sampled_state = torch.FloatTensor([])
        sampled_action = []
        sampled_reward = []
        sampled_next_state = torch.FloatTensor([])
        for data in sampled_data:
            #catはtorch.Tensorをリスト入れて渡すことで、それらを連結したTensorを返してくれる。0で行を追加となる
            sampled_state = torch.cat((sampled_state, data.state.view(1,-1)), 0)
            sampled_next_state = torch.cat((sampled_next_state, data.next_state.view(1,-1)), 0)
            sampled_action.append(data.action)
            sampled_reward.append(data.reward)
        

        print('sampled_state: ',sampled_state)
        print('sampled_next_state: ',sampled_next_state)
        print('sampled_action: ',sampled_action)
        print('sampled_reward: ',sampled_reward)

        sampled_state = encode_onehot(sampled_state, onehot_idx_list, onehot_len_list)
        print('sampled_state_encode_onehot: ',sampled_state)
        sampled_state = normalize_mask(sampled_state, onehot_idx_list, onehot_len_list)
        print('sampled_state_normalize_mask: ',sampled_state)

        sampled_next_state = encode_onehot(sampled_next_state, onehot_idx_list, onehot_len_list)
        print('sampled_next_state_encode_onehot: ',sampled_next_state)
        sampled_next_state = normalize_mask(sampled_next_state, onehot_idx_list, onehot_len_list)
        print('sampled_next_state_normalize_mask: ',sampled_next_state)

        sampled_action = torch.FloatTensor(sampled_action)
        sampled_reward = torch.FloatTensor(sampled_reward)
        
        print('sampled_action_after_transform: ',sampled_action)
        print('sampled_reward_after_transform: ',sampled_reward)

        #to GPU
        sampled_state = sampled_state.to(self.device)
        sampled_next_state = sampled_next_state.to(self.device)
        sampled_action = sampled_action.to(self.device)
        sampled_reward = sampled_reward.to(self.device)

        #dimで指定された軸(dim=1(列))に沿って、選択した行動を基にQ(s_t, a)を収集。
        state_action_values = self.policy_net(sampled_state).gather(1, sampled_action.unsqueeze(1).long())
        #target_netでは次の状態でのQ値を出す。ここではmaxを取る
        next_state_values = self.target_net(sampled_next_state).max(1)[0].detach()
        expected_state_action_values = (next_state_values * self.gamma) + sampled_reward
        # expected_state_action_valuesは
        # sizeが[batch_size]になっているから、unsqueezeで[batch_size x 1]へ
        criterion = nn.MSELoss()
        sampleLoss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
        self.optimizer.zero_grad()
        # 勾配の計算
        sampleLoss.backward()
        # error clipping
        for param in self.policy_net.parameters():
            #勾配の値を直接変更する
            #https://pytorch.org/docs/master/torch.html#torch.clamp
            param.grad.data.clamp_(-1, 1)
        # パラメータの更新
        self.optimizer.step()
        #lossから実数値を取り出す。
        sampleLoss = sampleLoss.item()
        #第一引数に元の数値、第二引数に桁数（何桁に丸めるか）を指定する。
        return round(float(sampleLoss), 3)

    def reward(self,reward_r):
        return 2*sigmoid(reward_r/100)-1

    def _insert_agent(self, user_id):
        japantime_now = get_japantime_now()
        japantime_now_str = date_to_date(japantime_now)
        #最初の保存でのデータは使えないので、pickled_replay_memory_itemID_valueListに[]を格納する
        pickled_replay_memory_itemID_valueList = pickle.dumps([])
        #insert_dictはdynamo_insert_itemメソッドで変数Itemに格納されている。
        insert_dict = {
            'user_id': int(user_id),
            'steps_done': int(self.steps_done),
            'replay_memory_memory': pickled_replay_memory_itemID_valueList,
            'create': japantime_now_str
        }

        print('steps_done: ', self.steps_done)
        print('create: ', japantime_now_str)
        print('insert agent: done')
        if user_id == 1:
            EXPORT_REPLAYMEMORY_FILE_NAME_1 = REPLAYMEMORY_DIRECTORY_NAME + japantime_now_str + '__usr' + str(user_id)
            IMPORT_REPLAYMEMORY_FILE_NAME_1 = EXPORT_REPLAYMEMORY_FILE_NAME_1
        else:
            EXPORT_REPLAYMEMORY_FILE_NAME_2 = REPLAYMEMORY_DIRECTORY_NAME + japantime_now_str + '__usr' + str(user_id)
            IMPORT_REPLAYMEMORY_FILE_NAME_2 = EXPORT_REPLAYMEMORY_FILE_NAME_2

        self._save_data_pickle(insert_dict,user_id)
        return True

    def _save_agent(self, userID, replay_memory_userID_valueList):
        japantime_now = get_japantime_now()
        japantime_now_str = date_to_date(japantime_now)
    
        pickled_replay_memory_itemID_valueList = pickle.dumps(replay_memory_itemID_valueList)
        
        update_dict = {
            'user_id': int(userID),
            'steps_done': int(self.steps_done),
            'replay_memory_memory': pickled_replay_memory_itemID_valueList
            'updated': japantime_now_str
        }
        self._save_data_pickle(update_dict,userID)
        print('saved agent: done')
        return True

    def _save_data_pickle(self,data,userID):
        if userID == 1:    
            file_name = EXPORT_REPLAYMEMORY_FILE_NAME_1
        else:
            file_name = EXPORT_REPLAYMEMORY_FILE_NAME_2
        with open(file_name,'wb') as f:
            f.write(pickle.dumps(data))
        return True

    def _read_data_pickle(self, userID):
        if userID == 1:
            file_name = IMPORT_REPLAYMEMORY_FILE_NAME_1
        else:
            file_name = IMPORT_REPLAYMEMORY_FILE_NAME_2
        try:
            with open(file_name, 'rb') as f:
                data = pickle.loads(f.read())
            return data
        except:
            return None

    def _report_agent(self):
        print('#######################')
        #print(get_japantime_now())
        print('k division: ', self.k_division)
        print('states number: ', self.states_number)
        print('epsilon start: ', self.eps_start)
        print('epsilon end: ', self.eps_end)
        print('eplison decay: ', self.eps_decay)
        print('gamma:', self.gamma)
        print('target update: ', self.target_update)
        print('memory length: ', self.memory_length)
        print('device: ', self.device)

    def get_network_fn(self, idx, flag):
        date_now = get_japantime_now() # util.py
        date_now_str = date_to_date(date_now)
        idx_str = str(idx)
        if flag:
            flag_str = 'T'
        else:
            flag_str = 'F'
        dir_name = PARAMETER_DIRECTORY_NAME + TODAYS_DATE_DIRECTORY_NAME
        tmp = date_now_str + '_' + idx_str + '_' + flag_str + '.pt'
        fn = {"policy":dir_name + 'policy_' + tmp, "target": dir_name + 'target_' + tmp}
        return fn

    def _save_network(self, idx, flag):
        fn = self.get_network_fn(idx, flag)
        EXPORT_POLICY_FILE_NAME = fn["policy"]
        EXPORT_TARGET_FILE_NAME = fn["target"]
        torch.save(agent.policy_net.state_dict(),EXPORT_POLICY_FILE_NAME)
        torch.save(agent.target_net.state_dict(),EXPORT_TARGET_FILE_NAME)
        return fn

    def _select_action(self, state, evaluation=False, ez_flg=False):
        state = state.to(self.device)
        if evaluation or ez_flg: # self play中
            print("######### policy net ###")
            print(self.policy_net)
            print(self.policy_net(state))
            with torch.no_grad():
                #(1)で列　[1]でmaxになっているindexを取得
                return self.policy_net(state).max(1)[1]
        else: # 学習中
            sample = random.random()
            #これはPyTorchのDQNチュートリアルから
            eps_threshold = self.eps_end + (self.eps_start - self.eps_end) *  math.exp(-1. * self.steps_done / self.eps_decay)
            print("######### policy net ###")
            print(self.policy_net)
            print(self.policy_net(state))
            if sample < eps_threshold:
                with torch.no_grad():
                    #(1)で列　[1]でmaxになっているindexを取得
                    return self.policy_net(state).max(1)[1]
            else:
                #ランダムセレクト
                return torch.tensor([random.randrange(self.actions_number) for i in range(len(state))], device=self.device, dtype=torch.long)

    def _run_agent(self, df_division, i_flg=False): # 学習させてloss, nextActionを取得, i_flgは各インターバル1回目の学習
        dim = df_division.shape
        #モデルに渡すagentの数
        self.numberOfProducts = dim[0]#len(df_division)
        self.batch_size = min(64,int(self.numberOfProducts/2))
        #batch_sizeが２未満だと、標準化するときにエラーとなってしまうため、self.batch_sizeを2以上にする。
        if self.batch_size < 2:
            self.batch_size = 2
        
        self.memory_length = 14*self.numberOfProducts
        #_optimize_modelを呼び出す回数 ＝ 勾配を求める回数
        #samplingCountは徐々に減らすようにした方がいいかもしれない
        self.samplingCount = int(self.numberOfProducts / self.batch_size) * 20

        print('numberOfProducts: ', self.numberOfProducts)
        print('batch_size: ', self.batch_size)
        print('memory_length: ', self.memory_length)
        print('samplingCount: ',self.samplingCount)

        #userId取得
        userIDList = [1,2]

        #steps_doneの中で最大値を取ってくる。 最大でないsteps_doneは在庫切れ、新しく登録された商品に該当する。
         #self.steps_done = dynamo_select_max_steps_done(db_agent, self.k_division)
        
        '''
        if i_flg: # epoch = 1のとき , ここでのepochは各インターバルでのepoch =1
            self._init_agent()
            #初回はpytorchのパラメータ保存ファイルがないので、loadしない。初回はsteps_done=0となる。
            if self.steps_done==0:
            #ここで楽観的初期化を行う
                self.policy_net.load_state_dict(model_state_dict)
                self.target_net.load_state_dict(model_state_dict)
            # if self.steps_done != 0:
            elif self.steps_done != 0:
                self._load_agent()
        '''
        
        if i_flg: # epoch = 1のとき , ここでのepochは各インターバルでのepoch =1
            self._init_agent()
            #初回はpytorchのパラメータ保存ファイルがないので、loadしない。初回はsteps_done=0となる。
            if self.steps_done==0:
                if IMPORT_POLICY_FILE_NAME != '' and IMPORT_TARGET_FILE_NAME != '': # importfile名が空でない, つまり一番最初から指定したパラメータで学習を行う
                    self._load_agent()
                else: # 完全にまっさらな状態から学習を始める
                    #ここで楽観的初期化を行う
                    self.policy_net.load_state_dict(model_state_dict)
                    self.target_net.load_state_dict(model_state_dict)
            # if self.steps_done != 0:
            elif self.steps_done != 0:
                self._load_agent()

        replay_memory_dic = {}
        #rowがない場合(dynamo_select_row_by_itemIDでNoneとなる)とreplay_memory_memoryの内容が古い場合、このリストにitemIDを追加する
        none_user_id_list = []
        #steps_doneがmaxでない(在庫切れなどでストップなど)場合、このリストにitemIDを追加する
        not_max_steps_done_user_id_list = []

        #replay_memoryをdynamoDBから読み込んで作成。
        #条件によって、not_max_steps_done_item_id_listとnone_item_id_listにitemIDを追加する
        #itemID毎に要素を取り出して、連結していく。
        #for itemID in itemIDList:
        '''
        for userID in userIDList:
            row = self._select_row_by_userID(fn_agent, int(userID))
            #rowがない場合はNoneとなる
            #2回目以降はreplay_memory_dicはdynamoDBから読み込むことができる。
            if row is not None:
                print("row is not None True")
                #steps_doneがmaxかどうか
                if row['steps_done'] == self.steps_done:
                    replay_memory_memory = row['replay_memory_memory'].value
                    replay_memory_memory = pickle.loads(replay_memory_memory)
                    #insertではreplay_memory_memoryに[]を格納している
                    if len(replay_memory_memory) > 0:
                        for i in range(len(replay_memory_memory)):
                            #int -> float
                            replay_memory_memory[i][0] = replay_memory_memory[i][0].float()
                            replay_memory_memory[i][2] = replay_memory_memory[i][2].float()
                    print(replay_memory_memory)
                    print(type(replay_memory_memory))
                    replay_memory_dic[userID-1] = replay_memory_memory
                #steps_doneがmaxでない、つまり古いValueなので、replay_memory_dic[userID]にNoneを格納しておく
                else:
                    not_max_steps_done_user_id_list.append(userID)
                    replay_memory_dic[userID-1] = None
            #rowがNoneの場合
            else:
                print("row is not None False")
                none_user_id_list.append(userID)
                replay_memory_dic[userID-1] = None
        '''
        # setps_doneが常にmaxであると願って...
        for userID in enumerate(userIDList):
            row = self._read_data_pickle(userID)
            if row is None:
                none_user_id_list.append(userID)
                replay_memory_dic[str(userID)] = None
            else:                
                replay_memory_dic[str(userID)] = pickle.loads(row['replay_memory_memory'])


        #replay_memory_itemID_valueListに要素の数が最大で何個入っているか求める。最大サイズをmaxLengthに格納する
        maxLength = 0
        for replay_memory_userID_valueList in replay_memory_dic.values():
            if replay_memory_userID_valueList is not None:
                length = len(replay_memory_userID_valueList)
                if maxLength < length:
                    maxLength = length

        #valueを取り出して、replay_memoryに格納していく
        #古いものから新しいものを入れていく
        for i in range(maxLength):
            for replay_memory_userID_valueList in replay_memory_dic.values():
                if replay_memory_userID_valueList is not None:
                    if len(replay_memory_userID_valueList) -1 >= i:
                        dayValue = replay_memory_userID_valueList[i]
                        #replay_memoryは_init_agentメソッドで初期化される。
                        #state, action, next_state, reward, userIDの順番
                        self.replay_memory.push(dayValue[0],dayValue[1],dayValue[2],dayValue[3],dayValue[4])

        #stateはbefore_(１日前)から取得
        state = torch.FloatTensor(df_division[:,:dim[1]/2])
        '''
        #actionを格納していくnumpyリスト
        actionList = np.zeros(len(df_division), dtype = int) 

        for index,product in enumerate(df_division.iterrows()):
            print("index",index)
            print(product[1].to_json(orient='records'))
            #beforeDailyPriceが0の場合（初回）はinitPriceに一番近い価格をkeyにしてactionを取得する
            if product[1].beforeDailyPrice == 0:
                #keyが価格、valueがaction
                action = self.makeNearInitPrice(product)
            else:
                #beforeDailyPriceからactionに変換する
                action = self._make_action_class_non_care_init(product[1])[product[1].beforeDailyPrice]
            actionList[index] = action
        actionList = torch.from_numpy(actionList)
        '''
        actionList = self.action_history.pop()

        
        #next_stateはfeatures(当日)から取得
        next_state = torch.FloatTensor(df_division[:,dim[1]/2:])
        '''
        before_daily_revenue = df_division['beforeDailyRevenue'].values
        before_daily_uv = df_division['beforeDailyUv'].values
        before_daily_uv[before_daily_uv == 0] = 1
        
        daily_revenue = df_division['dailyRevenue'].values
        daily_uv = df_division['dailyUv'].values
        # to avoid divide by zero
        daily_uv[daily_uv == 0] = 1

        sigmoid = nn.Sigmoid()
        #rewardの設計 https://openreview.net/pdf?id=HJMRvsAcK7 
        reward_r = torch.FloatTensor(daily_revenue)
        '''
        
        print('action: ',actionList)
        #print('reward: ',reward)

        #before_features_listの内容を追加する。辞書の更新とreplay_memoryの更新
        replay_memory_count = 0
        reward = np.array([])
        for i in range(len(state)):
            #ここで取り出される順番はitemIDListと対応している。
            #辞書からvalueListを取得。
            #初回の時と一旦ストップした商品はreplay_memoryには入れない。
            '''
            if itemIDList[i] in none_item_id_list or itemIDList[i] in not_max_steps_done_item_id_list:
                continue
            replay_memory_itemID_valueList = replay_memory_dic[itemIDList[i]]
            '''
            # reward
            reward[i] = self.reward(reward_r)

            if userIDList[i] in none_item_id_list or userIDList[i] in not_max_steps_done_item_id_list:
                # if true, 以下の処理は行われない
                continue

            replay_memory_itemID_valueList = replay_memory_dic[str(userIDList[i])]
            #追加するvalue
            #addValue = [state[i], actionList[i], next_state[i], reward[i],itemIDList[i]]
            addValue = [state[i], actionList[i], next_state[i], reward[i], userIDList[i]]
            #continueでない時、２回目以降などにくる。
            #valueListにappendする
            replay_memory_itemID_valueList.append(addValue)
            #更新したvalueListを格納する。
            #replay_memory_dic[itemIDList[i]] = replay_memory_itemID_valueList
            replay_memory_dic[str(userIDList[i])] = replay_memory_itemID_valueList
            replay_memory_count += 1
            #overWriteFlagがTrueの場合、上書きが発生した。辞書に対しても、先頭のValueに対して削除を行う必要がある。
            overWriteFlag,deleteItemID = self.replay_memory.push(state[i], actionList[i], next_state[i], reward[i],itemIDList[i])
            if overWriteFlag:
                replay_memory_dic[deleteItemID].pop(0)
        print("replay_memory_count: ",replay_memory_count)
        print("replay_memory_size: ",len(self.replay_memory))
        print("#############")
        print("replay_memory_memory")
        print(self.replay_memory.memory)
        #optimize_modelメソッドをsamplingCountだけ走らせる。samplingCountだけlossが求まり、パラメータが更新される。
        returnLoss = -1
        sumLoss = 0

        #self.samplingCountだけ勾配を求める
        for count in range(self.samplingCount):
            #学習
            sampleLoss = self._optimize_model()
            #if len(self.replay_memory) < self.batch_size: の時、return None
            if sampleLoss is None:
                break
            print('count',count)
            print('sampleLoss',sampleLoss)
            sumLoss += sampleLoss
        if sumLoss != 0:
            returnLoss = sumLoss / self.samplingCount
            self.averageLoss = returnLoss
        print('loss',returnLoss)
        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        #next_state_normalized = encode_onehot(next_state, onehot_idx_list, onehot_len_list)
        #next_state_normalized = normalize_mask(next_state_normalized, onehot_idx_list, onehot_len_list)

        # map to price
        new_action = np.array([])
        #next_stateからnew_actionが求まる　このnew_actionからnew_priceが求まり、これがreturnされる。
        for i in range(len(df_division)):
            new_action[i] = self._select_action(next_state[i])

        '''
        for idx, product in enumerate(df_division.iterrows()):
            #初回の時のnew_priceはinitPriceに一番近い値にする
            if product[1].itemId in none_item_id_list or product[1].itemId in not_max_steps_done_item_id_list:
                product_new_action = self.makeNearInitPrice(product)
                product_new_price = self._make_price_class_non_care_init(product[1])[int(product_new_action)]
                new_price = np.append(new_price,product_new_price)
            else:
                product_new_price = self._make_price_class_non_care_init(product[1])[int(new_action[idx])]
                new_price = np.append(new_price,product_new_price)
       '''
        #self.steps_done += 1

        for userID in enumerate(userIDList):
            if userID in none_user_id_list: # row is None.
                self._insert_agent(userID)
            '''
            elif userID in not_max_steps_done_user_id_list:
                print("IN not_max_steps_done_user_id_list")
                replay_memory_userID_valueList = []
                self._save_replay_memory(fn_agent,itemID,replay_memory_itemID_valueList,logNewPrice)
            '''
            else: # no plobrem
                replay_memory_itemID_valueList = replay_memory_dic[str(userID)]
                self._save_agent(userID,replay_memory_itemID_valueList)

        #print('run agent already exist wake up at ', self.steps_done)
        '''
        modelIDList = df_division['modelId'].values
        #userIDListを基にfor文を回し、取得したitemIDで辞書型のkeyにアクセスする。
        #取得したid,valueを基にdynamoDBに保存する。
        #for index,itemID in enumerate(itemIDList):
        for index,itemID in enumerate(userIDList):
            if itemID in none_item_id_list:
                self._insert_agent(db_agent,itemID)
            elif itemID in not_max_steps_done_item_id_list:
                print("IN not_max_steps_done_item_id_list")
                replay_memory_itemID_valueList = []
                logNewPrice = new_price[index]
                logModelID = modelIDList[index]
                self._save_agent(db_agent,itemID,replay_memory_itemID_valueList,logNewPrice,logModelID)
            else:
                replay_memory_itemID_valueList = replay_memory_dic[itemID]
                logNewPrice = new_price[index]
                logModelID = modelIDList[index]
                self._save_agent(db_agent,itemID,replay_memory_itemID_valueList,logNewPrice,logModelID)
        print('run agent already exist wake up at ', self.steps_done)
        '''
        self._report_agent()
        return new_action, returnLoss, reward

    def agent_learning(self, env, epochs, idx, evaluation=False): # 一定期間試合を行わせて学習をさせる
        epochs_done = 0 # 正しく実行された回数をカウント
        loss_per_epoch = [] # 試合ごとのloss (最終ターンでのlossを収集)

        try:
            # epochs の数だけ学習を行う
            # 流れ
            # 1.環境のリセット
            # 2.turnの数だけ各エージェントが行動とoptimizeを行う
            #  2.1 各エージェントの次の行動決定とoptimize
            #   2.1.1 ネットワークに突っ込むdata(特徴量)をまとめる
            #   2.1.2 楽観的初期化
            #   2.1.3 特徴量から行動を取得
            #  2.2 エージェントの移動先が重なっていないか判定し，行動を決定する
            #   2.2.1 重なっていなければデータを整理(行動を行う準備する)
            #   2.2.2 重なっていれば，両エージェントの行動をstayとする
            #  2.3 行動前に得点を取得
            #  2.4 行動させる
            epochs = EPOCHS
            for epc in range(epochs):
                # game start
                turn, length, width = env._start()
                before_features = []
                # turn の数だけ，行動を行う
                for t in range(turn):
                    if t == 0: # before_feature の初期化
                        before_features = torch.cat(
                            (env.get_features(t,1),env.get_features(t,2)),
                            dim = 0
                        )
                    else: # フィールドの得点を変える
                        env._changeField()

                    # 2エージェント分の特徴量をまとめる
                    now_features = torch.cat(
                        (env.get_features(env,t+1,1),env.get_features(env,t+1,2)),
                        dim=0 # 横長の配列を縦に並べる
                    )#前ターンの行動後(つまり現ターンの行動前)の特徴量

                    before_features = now_features # 次ターンのbefore_featuresに，現ターン行動前の特徴量を設定する
                    data = torch.cat(
                        (before_features, now_features),
                        dim = 0 # 配列を縦にくっつける
                    )
                    df_division = torch.cat(
                        (before_features, now_features),
                        dim = 1 # 配列を縦にくっつける
                    )


                    # for 楽観的初期化
                    #k_division = 17 # 行動数
                    #states_num = 18 #len(data) 特徴量の大きさ(skalar)
                    model = param_init_model(data, self.k_division, self.states_num, ite = 20, epoch = 5)

                    # 特徴量をもとにネットワークから行動を取得
                        # run_agent() で次の行動を決める(実際に行動はしない)
                    #agent = DQNAgent(self.k_division)
                    if not evaluation: # 学習中
                        # db_agent, df_division
                        if epc == 0:
                            new_action, loss, reward = self._run_agent(df_division, model.state_dict(),flg=True) # new_action は数字を返す
                        else:
                            new_action, loss, reward = self._run_agent(df_division, model.state_dict()) # new_action は数字を返す
                    else: # self play
                        dim = df_division.shape
                        next_state = torch.FloatTensor(df_division[:,dim[1]/2:])
                        new_action = np.array([])
                        for i in range(len(df_division)):
                            new_action[i] = self._select_action(next_state[i])

                    # item_id_division:usrID(のリスト), new_price_division: usrの次の行動("n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード)
                    usr_id_division = np.array([1,2])
                    df_dic = {'usrID': usr_id_division, 'now_eval': np.array([idx]*2), 'num_game': np.array([game_num]),'now_game': np.array([g_num]*2), 'num_turn': np.array([turn]*2),'now_turn': np.array([t+1]*2), 'calcAction': new_action, 'Loss': np.array([loss]*2), 'reward': reward}#* len(item_id_division))}
                    #df_dic = {'calcAction': new_action, 'Loss': np.array([loss]*2), 'reward': reward}#* len(item_id_division))}

                    df_dic = pd.DataFrame(data=df_dic)
                    df_runLog = df_runLog.append(df_dic, sort=False)

                    # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
                    df_action = {}
                    df_action["motion"] = []
                    df_action["direction"] = []
                    df_action["is_possible"] = []
                    #df_action["n_position"] = []

                    for usrID in enumerate(usr_id_division):
                        code, data, next_pos = env._judgeDirection(usrID,new_action[usrID-1])
                        df_action["do_motion"].append(data['motion'])
                        df_action["do_direction"].append(data['direction'])
                        df_action["is_possible"].append(code)
                        #df_action["n_position"].append(next_pos)
                
                    # エージェントの移動先が重なってるか，いないかを判定し行動を決定
                    cnf, m_data = env.check_action(df_action)

                    df_action["is_possible"] = np.array([int(i) for i in enumerate(df_action["is_possible"])])
                    df_dic.update(df_action)
                    df_dic["is_confliction"] = np.array([cnf]*2)

                    # 移動前に得点を取得
                    point_before_moving = env._calcPoint()
                    # 判定後に実際に移動させる
                    env.do_action(m_data[0])
                    env.do_action(m_data[1])
                    # 行動を保存しておく
                    self.action_history.append(m_data)  
                    # 移動後の得点を取得
                    point_after_moving = env._calcPoint()

                    # logを保存
                    if LOG_IN_LEARNING:
                        if epc == 0:
                            EXPORT_LEARN_HISTORY_FILE_NAME = 'learn_history_' + str(idx) + '_' + str(epc) + '_' + TODAYS_DATE + '.csv'
                            df.to_csv(LEARN_HISTORY_DIRECTORY_NAME + EXPORT_LEARN_HISTORY_FILE_NAME, encoding='shift_jis')
                        else:
                            df.to_csv(LEARN_HISTORY_DIRECTORY_NAME + EXPORT_LEARN_HISTORY_FILE_NAME, mode='a', header=False, encoding='shift_jis')
                    
                    if t+1 == turn:
                        loss_per_epoch.append(loss)
                epochs_done += 1

            fn = self._save_network(fn)
            np_loss = np.array(loss_per_epoch)
            logs = {"num_sets": str(idx),"num_epoch": str(epochs),"epochs_done": str(epochs_done), "loss_max":  np.max(np_loss), "loss_max_idx": np.argmax(np_loss), "loss_median": np.median(np_loss),"loss_min": np.min(np_loss),"loss_min_idx":np.argmin(np_loss),"loss_average":np.average(np_loss),"policy":fn["policy"], "target":fn["target"]}
            # logの保存
            return True, logs

        except:
            fn = self._save_network(fn)
            logs = {"num_sets": str(idx),"num_epoch": str(epochs),"epochs_done": str(epochs_done), "loss_max":  np.max(np_loss), "loss_max_idx": np.argmax(np_loss), "loss_median": np.median(np_loss),"loss_min": np.min(np_loss),"loss_min_idx":np.argmin(np_loss),"loss_average":np.average(np_loss),"policy":fn["policy"], "target":fn["target"]}
            # logの保存
            return False, logs

    def judgeWorL(self,df_dic):
        if df_dic['after_totalpoint'][0] > df_dic['after_totalpoint'][1]: # agentの勝利
            return True
        elif df_dic['after_totalpoint'][0] < df_dic['after_totalpoint'][1]:
            return False
        elif df_dic['after_totalpoint'][0] == df_dic['after_totalpoint'][1]:
            if df_dic['after_areapoint'][0] > df_dic['after_areapoint'][1]:
                return True
            else:
                return False

    def agent_evaluation(self, env, agent, opponent, idx)):  # self playを行う
        e_log = {'agent_won':0, 'opponent_won':0, 'num_game': NUMBER_OF_SELFPLAY}
        try:
            self._init_agent(flg=True)
            self._load_agent(file_name=[agent, opponent]flg=True)
            games_done = 0
            games_num = NUMBER_OF_SELFPLAY

            for g_num in range(game_num):
                before_features = []
                turn, length, width = env._start()
                # turn の数だけ，行動を行う
                for t in range(turn):
                    if t == 0: # before_feature の初期化
                        before_features = torch.cat(
                            (env.get_features(t,1),env.get_features(t,2)),
                            dim = 0
                        )
                    else: # フィールドの得点を変える
                        env._changeField()

                    # 2エージェント分の特徴量をまとめる
                    now_features = torch.cat(
                        (env.get_features(env,t+1,1),env.get_features(env,t+1,2)),
                        dim=0 # 横長の配列を縦に並べる
                    )#前ターンの行動後(つまり現ターンの行動前)の特徴量

                    before_features = now_features # 次ターンのbefore_featuresに，現ターン行動前の特徴量を設定する
                    data = torch.cat(
                        (before_features, now_features),
                        dim = 0 # 配列を縦にくっつける
                    )
                    df_division = torch.cat(
                        (before_features, now_features),
                        dim = 1 # 配列を縦にくっつける
                    )

                    dim = df_division.shape
                    next_state = torch.FloatTensor(df_division[:,dim[1]/2:])
                    new_action = np.array([])
                    with torch.no_grad():
                        new_action[0] = self.policy_net_a(next_state[0]).max(1)[1]
                        new_action[1] = self.policy_net_a(next_state[1]).max(1)[1]
                    
                    # item_id_division:usrID(のリスト), new_price_division: usrの次の行動("n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード)
                    usr_id_division = np.array([1,2])
                    df_dic = {'usrID': usr_id_division, 'now_eval': np.array([idx]*2), 'num_game': np.array([game_num]),'now_game': np.array([g_num]*2), 'num_turn': np.array([turn]*2),'now_turn': np.array([t+1]*2), 'calcAction': new_action}#* len(item_id_division))} # num_ : 総数(総ターンなど), now_: 現在(現在は5ターン目など)
                    #df_dic = {'calcAction': new_action, 'Loss': np.array([loss]*2), 'reward': reward}#* len(item_id_division))}

                    df_dic = pd.DataFrame(data=df_dic)

                    # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
                    df_action = {}
                    df_action["motion"] = []
                    df_action["direction"] = []
                    df_action["is_possible"] = []
                    #df_action["n_position"] = []

                    for usrID in enumerate(usr_id_division):
                        code, data, next_pos = env._judgeDirection(usrID,new_action[usrID-1])
                        df_action["do_motion"].append(data['motion'])
                        df_action["do_direction"].append(data['direction'])
                        df_action["is_possible"].append(code)
                        #df_action["n_position"].append(next_pos)
                
                    # エージェントの移動先が重なってるか，いないかを判定し行動を決定
                    cnf, m_data = env.check_action(df_action)

                    df_action["is_possible"] = np.array([int(i) for i in enumerate(df_action["is_possible"])])
                    df_dic.update(df_action)
                    df_dic["is_confliction"] = np.array([cnf]*2)
                    
                    
                    # 移動前に得点を取得
                    point_before_moving = env._calcPoint()
                    # 判定後に実際に移動させる
                    env.do_action(m_data[0])
                    env.do_action(m_data[1])
                    # 行動を保存しておく
                    self.action_history.append(m_data)     
                    # 移動後の得点を取得
                    point_after_moving = env._calcPoint()

                    df_dic['before_tilepoint'] = np.array([point_before_moving[0],point_before_moving[3]])
                    df_dic['before_areapoint'] = np.array([point_before_moving[1],point_before_moving[4]])
                    df_dic['before_totalpoint'] = np.array([point_before_moving[2],point_before_moving[5]])
                    df_dic['after_tilepoint'] = np.array([point_after_moving[0],point_after_moving[3]])
                    df_dic['after_areapoint'] = np.array([point_after_moving[1],point_after_moving[4]])
                    df_dic['after_totalpoint'] = np.array([point_after_moving[2],point_after_moving[5]])
                    # logを保存
                    df = pd.DataFrame(df_dic)
                    if g_num==1:
                        EXPORT_EVAL_HISTORY_FILE_NAME = 'eval_history_' + str(idx) + '_' + str(g_num) + '_' + TODAYS_DATE + '.csv'
                        df.to_csv(EVAL_HISTORY_DIRECTORY_NAME + EXPORT_EVAL_HISTORY_FILE_NAME, encoding='shift_jis')
                    else:
                        df.to_csv(EVAL_HISTORY_DIRECTORY_NAME + EXPORT_EVAL_HISTORY_FILE_NAME, mode='a', header=False, encoding='shift_jis')
                
                if self.judgeWorL(df_dic):
                    e_log['agent_won'] += 1
                else:
                    e_log['opponent_won'] += 1
                games_done += 1

            return True
        except:
            return False

    def select_model(self, a_logs, first=False, e_logs=None):
        if e_logs is not None: # 2回目(self play終了後)に呼ばれるとき
            if float(int(e_logs['agent_won']) / int(e_logs['num_game'])) >= 0.5: # agentの勝率が5割以上
                return {"policy":a_logs["policy"], "target":a_logs["target"]}
            else:
                return {"policy":e_logs["oppo_policy"], "target":a_logs["oppo_target"]}
        else: # 1回目(self play前)に呼ばれるとき
            if first: # 初回のself play
                self.agent_history[0].append(a_logs['loss_median'])
                self.agent_history[1].append(a_logs['target'])
                self.agent_history[2].append(a_logs['policy'])
                return {'oppo_target': a_logs["policy"], 'oppo_policy': a_logs["target"]}
            else:
                oppo_target_name = self.agent_history[1][0]
                oppo_policy_name = self.agent_history[2][0]
                if a_logs['loss_median'] < self.agent_history[0][0]:
                    self.agent_history[0][0] = a_logs['loss_median']
                    self.agent_history[1][0] = a_logs['target']
                    self.agent_history[2][0] = a_logs['policy']
                return {'oppo_target': oppo_target_name, 'oppo_policy': oppo_policy_name}

    # e_logs = {'interval': str(num_selfPlay), 'n_times': str(n_times), 'num_agent_won': int(won)}
    # opponent = {'oppo_target':, 'oppo_policy'}
    def process(self, env, oppo=None): # 学習開始からself playを経て学習終了まで
        now_exec = np.array([])
        num_agent_won = np.array([])
        num_opponent_won = np.array([])
        agent_won = np.array([])

        try:
            for idx in range(NUMBER_OF_SETS):
                now_exec = np.append(now_exec, idx)
                result, a_logs = self.agent_learning(env, idx) # 学習
                if not result:
                    return False
                # 対戦相手の選択    
                if oppo is not None: # 指定したagentと戦わせたい場合
                    opponent = oppo # {"policy":a_logs["policy"], "target":fn["target"]} の形式
                elif idx == 0: # 初回のself play
                    opponent = self.select_model(a_logs=a_logs,first=True)
                else: # 対戦相手を過去の中から選ぶ
                    opponent = self.select_model(a_logs)

                agent = {"policy":a_logs["policy"], "target":a_logs["target"]}
                result, e_logs = self.agent_evaluation(agent, opponent) # self play
                if not result:
                    return False

                num_agent_won = np.append(num_agent_won, e_logs['agent_won'])
                num_opponent_won = np.append(num_opponent_won, e_logs['opponent_won'])
                if e_logs['agent_won'] > e_logs['opponent_won']:
                    agent_won = np.append(agent_won, 1)  
                else:
                    agent_won = np.append(agent_won, 0)  
                
                if oppo is not None: # 指定したagentと戦わせる場合は，最初に生成したagentをずっと成長させる
                    IMPORT_POLICY_FILE_NAME = a_logs['target']
                    IMPORT_TARGET_FILE_NAME = a_logs['policy']
                else:
                    e_logs.update(opponent)
                    next_agent = self.select_model(a_logs=a_logs, e_logs=e_logs)
                    IMPORT_POLICY_FILE_NAME = next_agent['target']
                    IMPORT_TARGET_FILE_NAME = next_agent['policy']                


                self.steps_done += 1

            df_Logs = {'num_sets':np.array([NUMBER_OF_SETS]*NUMBER_OF_SETS), 'num_epochs': np.array([EPOCHS]*NUMBER_OF_SETS), 'num_games_per_selfplay': np.array([NUMBER_OF_SELFPLAY]*NUMBER_OF_SETS)}
            df_Logs['now_exec'] = now_exec
            df_Logs['num_agent_won'] = num_agent_won
            df_Logs['num_opponent_won'] = num_opponent_won
            df_Logs['agent_won'] = agent_won

            df = pd.DataFrame(df_Logs)
            EXPORT_NAME = EVAL_HISTORY_DIRECTORY_NAME + 'WoL_history_' + TODAYS_DATE + '.csv'
            df.to_csv(EXPORT_NAME, encoding='shift_jis')

            return True
        except:
            #num_done = min(len(now_exec),len(num_agent_won),len(num_opponent_won),len(agent_won))
            df_Logs = {'num_sets':np.array([NUMBER_OF_SETS]*self.steps_done), 'num_epochs': np.array([EPOCHS]*self.steps_done), 'num_games_per_selfplay': np.array([NUMBER_OF_SELFPLAY]*self.steps_done)}
            df_Logs['now_exec'] = np.delete(now_exec,len(now_exec)-1)
            df_Logs['num_agent_won'] = num_agent_won
            df_Logs['num_opponent_won'] = num_opponent_won
            df_Logs['agent_won'] = agent_won

            df = pd.DataFrame(df_Logs)
            EXPORT_NAME = EVAL_HISTORY_DIRECTORY_NAME + 'WoL_history_' + TODAYS_DATE + '.csv'
            df.to_csv(EXPORT_NAME, encoding='shift_jis')    

            return False

    def main(self):
        env = jinGAME()
        res = self.process(env)
        if not res:
            print('see log file')
        else:
            print('done')


