import requests
import random

class jinGameAPI():
    def __init__(self,port_num=8000):
        self.url = 'http://localhost:' + str(port_num)        

    def _start(self): # game start
        url = self.url + '/start'
        response = requests.post(url)
        # ゲーム情報(ターン数，タテ・ヨコのサイズ，得点フィールド，ユーザーフィールド)の取得と整理
        f = response.text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
        iv_list = [int(i) for i in f.split()] #listing initial value
        self.turn = iv_list[0] 
        self.length = iv_list[1] 
        self.width = iv_list[2]
        pointfield = []
        for i in range(self.length * self.width):
            pointfield.append(iv_list[i + 3])
        
        return self.turn,(self.length,self.width),pointfield

    def _move(self,usr,action): # move
        url = self.url + '/move'
        data = {
            'usr': str(usr),
            'd': self.num2str_action(action)
        }
        response = requests.post(url, data=data)

    def _remove(self,usr,action): # remove panel
        url = self.url + '/remove'
        data = {
            'usr': str(usr),
            'd': self.num2str_action(action)
        }
        response = requests.post(url, data=data)

    def _getField(self): # get point field, user field
        url = self.url + '/show'
        f = requests.post(url).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
        iv_list = [int(i) for i in f.split()]
        uf = []
        for i in range(self.length):
            l = []
            for j in range(self.width):
                l.append(iv_list[self.length* self.width + self.width * i + j])
            uf.append(l)
        pf = []
        for i in range(self.length):
            l = []
            for j in range(self.width):
                l.append(iv_list[self.width * i + j])
            pf.append(l)
        return pf,uf

    def _calcPoint(self): # calculate point
        url = self.url + '/pointcalc'
        response = requests.post(url).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
        iv_list = [int(i) for i in response.split()]
        return iv_list # [tile point 1, field point 1, total point 1, tile point 2, field point 2, total point 2]

    def _judgeDirection(self,usr,action): # judge direction 
        url = self.url + '/judgedirection'
        data = {
            'usr': str(usr),
            'd': self.num2str_action(action)
        }
        f = requests.post(url, data = data).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
        iv_list = [i for i in f.split()]
        il = [int(iv_list[1]),int(iv_list[0])] # [y(row),x(column)]

        if iv_list[2] == "Error": # out of field
            return "1"
        elif iv_list[2] == "is_panel": # is pannel
            return "2"
        elif iv_list[2] == "is_user": # is user
            return "3"
        else: # no plobrem
            return "4"

    def _changeField(self): # change field 
        url = self.url + '/change'
        f = requests.post(url)

    def _getPosition(self, usr): # get position
        url = self.url + '/usrpoint'
        data = {
          'usr': str(usr)
        }
        response = requests.post(url, data=data)
        f = response.text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
        pos_array =[int(i) for i in f.split()]
        return pos_array  # [x(column), y(row)]


    def num2str_action(self, action): # convert number into string
        if action == 0:
            return "lu"
        elif action == 1:
            return "u"
        elif action == 2:
            return "ru"
        elif action == 3:
            return "l"
        elif action == 4:
            return "z"
        elif action == 5:
            return "r"
        elif action == 6:
            return "ld"
        elif action == 7:
            return "d"
        elif action == 8:
            return "rd"