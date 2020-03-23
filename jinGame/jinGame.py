import sys
sys.path.append('../jinGame/api-src/')
from api_jintori import *

class jinGAME():
    def __init__(self,port_num):
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

    def num2str_action(self,n_action):
    if n_action < 9:
        motion = "move"
    elif n_action == 4:
        return "stay", "z"
    else:
        motion = "remove"

    n_action += 1

    if n_action % 9 == 1:
        direc = "lu"
    elif n_action % 9 == 2:
        direc = "u"
    elif n_action % 9 == 3:
        direc = "ru"
    elif n_action % 9 == 4:
        direc = "l"
    elif n_action % 9 == 6:
        direc = "r"
    elif n_action % 9 == 7:
        direc = "ld"
    elif n_action % 9 == 8:
        direc = "d"
    elif n_action % 9 == 0:
        direc = "rd"

    return motion, direc