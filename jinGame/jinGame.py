import sys
sys.path.append('../jinGame/api-src/')
from api_jintori import *

def get_dim_list(li): # 2次元配列(list)のshapeを取得
    return [len(li),len([len(v) for v in li])]

class jinGAME():
    def __init__(self,port_num=8000):
        self.domain = 'http://localhost:' + str(port_num)

    def _start(self):
        self.turn,(self.length,self.width),pointfield = s_start(self.domain)
        return self.turn,self.length,self.width

    def _move(self,usr,action):
        s_move(self.domain,usr,action)
    
    def _remove(self,usr,action):
        s_remove(self.domain,usr,action)

    def _getField(self):
        pf, uf = s_getField(self.domain,self.length,self.width)
    
    def _calcPoint(self):
        p_list = s_calcPoint(self.domain)
        return p_list

    def _judgeDirection(self,usr,action):
        ret_code, data, next_pos = s_judgeDirection(self.domain,usr,action)
        return ret_code, data, next_pos

    def _changeField(self):
        s_changeField(self.domain)

    def _getPosition(self,usr):
        pos_list = s_getPosition(self.domain,usr)

    def check_action(self,action):  # 行動先が被っていないか判定し，実際に行う行動を決定する
        # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
        if action["n_position"][0] == action["n_position"][1]: # 行動先がかぶるとき
            usr1_data = {'motion':"move", "lists": [1,4]}
            usr2_data = {'motion':"move", "lists": [2,4]}
            m_data = [usr1_data,usr2_data]
            return False, m_data
        else:
            return True, self.adjust_data(action)

    def adjust_data(self, action): # do_actionで使うためのデータを修正
        # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
        data = []
        for i in range(2):
            if action["is_possible"][i]==str(1): # out of field
                t_data = {'motion':action["motion"][i],'lists':[i,4]}
            elif action["is_possible"][i]==str(2): # is_panel
                t_data = {'motion':action["motion"][i],'lists':[i,4]}
            elif action["is_possible"][i]==str(3): # is_user
                if action["motion"][i] == "move":
                    t_data = {'motion':action["motion"][i],'lists':[i,4]}
                elif action["motion"][i] == "remove":
                    t_data = {'motion':action["motion"][i],'lists':[i,action["direction"][i]]}
            elif action["is_possible"][i]==str(4): # no_panel
                t_data = {'motion':"move",'lists':[i,4]}
            else: # no plobrem
                t_data = t_data = {'motion':action["motion"][i],'lists':[i,action["direction"][i]]}
            data.append(t_data)
        return data

    def do_action(self,m_data): # serverにactionを投げる
        if m_data['motion'] == "move":
            self._move(*m_data['lists'])
        elif m_data['motion'] == "remove":
            self._remove(*m_data['lists'])

    def get_around_point(self, pf,x,y): # 特徴量(自分周辺のポイント)
        # x,y は座標
        dim = get_dim_list(pf)
        if x==0 or x == dim[0]-1 or y==0 or y == dim[1]-1:
            p_list = [[-10] * 3 for i in [1] * 3]
            for i in range(1,4):
                if i==1 and y-i < 0:
                    pass
                elif i==3 and y+1 == dim[1]:
                    pass
                else:
                    yi = 2-i
                    for j in range(1,4):
                        if j==1 and x-j < 0:
                            pass
                        elif j==3 and x+1 == dim[0]:
                            pass
                        else:
                            xj = 2-j
                            p_list[i-1][j-1] = int(pf[y-yi][x-xj])
            p_list = sum(p_list, [])
        else:
            p_list = []
            for i in range(1,4):
                yi = 2-i
                for j in range(1,4):
                    xj = 2-j
                    p_list.append(int(pf[y-yi][x-xj]))
        
        return p_list

    def get_features(self,turn,usr): # 特徴量をserverから取得
        data = []
        if turn == 0:
            data = [0] * 18
        else:
            a_pos_list = self._getPosition(usr)
            a_pos = wid*(a_pos_list[1]) + a_pos_list[0] # 味方位置をナンバリング (0~width*length-1)
            if usr==1:
                b_usr = 2
                idx = 0
            else:
                b_usr = 1
                idx = 3
            b_pos_list = self._getPosition(b_usr)
            b_pos = wid*(b_pos_list[1]) + b_pos_list[0] # 相手位置をナンバリング (0~width*length-1)

            data = [self.turn, turn, self.length, self.width, a_pos, b_pos] # len(data) = 6

            pf,uf = self._getField()
            around_point = self.get_around_point(pf,*a_pos_list) # 周辺のポイント
            data.extend(around_point) # len(data) = 6 + 9 = 15
            #b_around_point = self.get_around_point(pf,*b_pos_list)
            p_list = self._calcPoint()
            point = p_list[idx:idx+3] # 自分のポイント
            data.extend(point) # len(data) = 15+3 = 18

        df_data = pd.DataFrame([data])
        data_tch = torch.from_numpy(np.array(df_data)).float()
        return data_tch