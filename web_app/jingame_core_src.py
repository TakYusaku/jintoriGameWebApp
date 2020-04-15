import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api_jintori as aj
from jinGame import jin_jinGame as jj
from jinGame import jin_NN as NN
from jingame_consts import *

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class web_jinGameAI():
    def __init__(self, target_filename, policy_filename,is_epszero):
        self.target_filename = target_filename
        self.policy_filename = policy_filename
        self.is_epszero = is_epszero
        self.states_number = 27
        self.actions_number = 17
        self.k_division = 17
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _init_agent(self):
        if self.is_epszero:
            self.policy_net = NN.DQN_epsZero(self.states_number, self.actions_number).to(self.device)
            self.target_net = NN.DQN_epsZero(self.states_number, self.actions_number).to(self.device)
        else:
            self.policy_net = NN.DQN(self.states_number, self.actions_number).to(self.device)
            self.target_net = NN.DQN(self.states_number, self.actions_number).to(self.device)            
        self.target_net.eval()
    
    def _load_agent(self):
        self.policy_net.load_state_dict(torch.load(self.policy_filename))
        self.target_net.load_state_dict(torch.load(self.target_filename)) 

    def _select_action(self, state): # ez_flg は epsilon-zero 用フラグ
        state = state.to(self.device)
        with torch.no_grad():
            #(1)で列　[1]でmaxになっているindexを取得
            return self.policy_net(state).max(1)[1]

class web_jinGame():
    def __init__(self, domain):
        # web_app のアドレス
        self.domain = domain
        self.jinGAME = jj.jinGAME(8008)
        self.ai = web_jinGameAI(target_filename=TARGETNET_FILENAME, policy_filename=POLICYNET_FILENAME, is_epszero=True)
        self.ai._init_agent()
        self.ai._load_agent()
        self.ai_before_features = []
        self.human_action_memory = [[],[]]

    def _web_init(self):
        self.player = '' # 何かしらつかうなら
        self.now_turn = 1

    def _start_game(self):
        self.turn, length, width = self.jinGAME._start()
        self.now_turn = 1
        data = self.get_send_data(code=0)
        return data

    def _turn_count(self):
        self.now_turn += 1

    def _is_finished(self):
        if self.now_turn == self.turn:
            return True
        else:
            return False

    def is_right_position(self, next_pos, now_pos):
        dx = next_pos[0]-now_pos[0]
        dy = next_pos[1]-now_pos[1]
        if abs(dx)==0 or abs(dx)==1:
            if abs(dy)==0 or abs(dy)==1:
                return True, self.coor2action_num(dx, dy)
            else:
                return False , None
        else:
            return False , None

    def _process(self, respond): # game進行中
        '''
        value = {
            'next_pos': position,
            'motion': action,
                    };
        '''
        # playerが入力したactionと次のposition
        player_next_pos = respond['next_pos']
        player_motion = respond['motion']
        # playerの現在のposition
        player_now_pos = self.jinGAME._getPosition(1)
        # player が正しいactionを選択したか?
        res, player_action = self.is_right_position(player_next_pos, player_now_pos)
        if not res: # 正しいactionを選択しなかった場合
            data = self.get_send_data(code=-1)
            return False, data
        
    
        # 正しい選択をした場合
        ## ai の特徴量を取得する
        if self.now_turn == 1: # before_feature の初期化
            self.ai_before_features.append(self.jinGAME.get_features(self.now_turn-1,2))

        ai_now_features = self.jinGAME.get_features(self.now_turn,2)
        ai_df_division = torch.cat(
            (self.ai_before_features[0], ai_now_features),
            dim = 1 # 配列を縦にくっつける
        )        
        self.ai_before_features[0] = ai_now_features

        dim = ai_df_division.shape
        # 特徴量のまとめ
        ai_next_state = torch.FloatTensor(ai_df_division[:,int(dim[1]/2):])

        # aiの行動を取得
        ai_new_action = self.ai._select_action(ai_next_state)
        ai_new_action = np.array([ai_new_action])
        
        # 行動の判別
        player_code, player_data, player_next_pos = self.jinGAME._judgeDirection(1, player_action, motion=player_motion)
        
        ai_code, ai_data, ai_next_pos = self.jinGAME._judgeDirection(2, ai_new_action[0])

        # エージェントの移動先が重なってるか，いないかを判定し行動を決定
        dic_action = {
            'now_position': [player_now_pos, self.jinGAME._getPosition(2)],
            'next_position': [player_next_pos, ai_next_pos],
            'do_motion': [player_data['motion'], ai_data['motion']],
            'do_direction': [player_data['d'], ai_data['d']],
            'is_possible': [player_code, ai_code],
        }
        '''
        dic_action = {
            'now_position': [player_now_pos, self.jinGAME._getPosition(2)],
            'next_position': [player_next_pos, self.jinGAME._getPosition(2)],
            'do_motion': [player_data['motion'], 'move'],
            'do_direction': [player_data['d'], 'z'],
            'is_possible': [player_code, '5'],
        }
        '''
        cnf, m_data, not_use = self.jinGAME.check_action(dic_action)

        
        if player_code == '5' or (player_code == "4" and player_motion=="remove"):
            # 行動を実行
            for i in range(2):
                self.jinGAME.do_action(m_data[i])
        else: # player_code is 1(out of field),2(rem:no panel),3(mov:is panel),4(mov:is user) (この4つはweb上では起こらないはず), 
            data = self.get_send_data(code=-2)          
            return False, data
        
        # フィールドの得点を変える
        self.jinGAME._changeField()
        # ターンを進める
        self._turn_count()
        # 送りデータの取得
        data = self.get_send_data(code=0)

        return True, data

    def get_send_data(self,code):
        #### 送るデータの整理
        point = self.jinGAME._calcPoint()
        pf, uf = self.jinGAME._getField()
        data = {
            'code': code,
            'turn':self.turn,
            'is_finished':None,                                                                                                                                                           
            'now_turn':self.now_turn,
            'now_point':point,
            'pf':pf,
            'uf':uf
        }
        if code==0:
            data['is_finished'] = self._is_finished()
        return data

    def get_send_data_human(self, code, usr):
        #### 送るデータの整理
        point = self.jinGAME._calcPoint()
        pf, uf = self.jinGAME._getField()
        data = {
            'code': code,
            'turn':self.turn,
            'is_finished':None,                                                                                                                                                           
            'now_turn':self.now_turn,
            'now_point':point,
            'next_usr':usr,
            'pf':pf,
            'uf':uf
        }
        if code==0:
            data['is_finished'] = self._is_finished()
        return data

    def _process_human(self, respond):
        if respond['usr']==1:
            player_next_pos = respond['next_pos']
            player_motion = respond['motion']
            # playerの現在のposition
            player_now_pos = self.jinGAME._getPosition(1)
            # player が正しいactionを選択したか?
            res, player_action = self.is_right_position(player_next_pos, player_now_pos)
            if not res: # 正しいactionを選択しなかった場合
                data = self.get_send_data_human(code=-1,usr=1)
                return False, data
            else:
                self.human_action_memory[0].append(respond)
                self.human_action_memory[1].append(player_action)
                data = self.get_send_data_human(code=0,usr=2)
                return True, data         
        else:
            player2_next_pos = respond['next_pos']
            player2_motion = respond['motion']
            # playerの現在のposition
            player2_now_pos = self.jinGAME._getPosition(2)
            # player が正しいactionを選択したか?
            res, player2_action = self.is_right_position(player2_next_pos, player2_now_pos)
            if not res: # 正しいactionを選択しなかった場合
                data = self.get_send_data_human(code=-1,usr=2)
                return False, data
            else:
                # 行動の判別
                usr1_respond = self.human_action_memory[0][0]
                player1_action = self.human_action_memory[1][0]
                player1_code, player1_data, player1_next_pos = self.jinGAME._judgeDirection(1, player1_action, motion=usr1_respond['motion'])
                player2_code, player2_data, player2_next_pos = self.jinGAME._judgeDirection(2, player2_action, motion=player2_motion)
                        # エージェントの移動先が重なってるか，いないかを判定し行動を決定
                dic_action = {
                    'now_position': [self.jinGAME._getPosition(1), self.jinGAME._getPosition(2)],
                    'next_position': [player1_next_pos, player2_next_pos],
                    'do_motion': [player1_data['motion'], player2_data['motion']],
                    'do_direction': [player1_data['d'], player2_data['d']],
                    'is_possible': [player1_code, player2_code],
                }
                cnf, m_data, not_use = self.jinGAME.check_action(dic_action)

                if player1_code == '5' or (player1_code == "4" and usr1_respond['motion']=="remove"):
                    if player2_code == '5' or (player2_code == "4" and player2_motion=="remove"):
                        # 行動を実行
                        for i in range(2):
                            self.jinGAME.do_action(m_data[i])
                    else: # player_code is 1(out of field),2(rem:no panel),3(mov:is panel),4(mov:is user) (この4つはweb上では起こらないはず), 
                        data = self.get_send_data_human(code=-2,usr=2)          
                        return False, data
                else: # player_code is 1(out of field),2(rem:no panel),3(mov:is panel),4(mov:is user) (この4つはweb上では起こらないはず), 
                    data = self.get_send_data_human(code=-2,usr=1)          
                    return False, data

                # フィールドの得点を変える
                self.jinGAME._changeField()
                # ターンを進める
                self._turn_count()
                # 送りデータの取得
                data = self.get_send_data_human(code=0,usr=1)
                self.human_action_memory = [[],[]]
                return True, data




    def coor2action_num(self, dx, dy):
        if dx==-1 and dy==-1:
            return "0"
        elif dx==0 and dy==-1:
            return "1"
        elif dx==1 and dy==-1:
            return "2"
        elif dx==-1 and dy==0:
            return "3"
        elif dx==0 and dy==0:
            return "4"
        elif dx==1 and dy==0:
            return "5"
        elif dx==-1 and dy==1:
            return "6"
        elif dx==0 and dy==1:
            return "7"
        elif dx==1 and dy==1:
            return "8"
