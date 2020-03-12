import requests
import random


def _start(port_num): # game start
    url = 'http://localhost:' + port_num + '/start'
    response = requests.post(url)
    # ゲーム情報(ターン数，タテ・ヨコのサイズ，得点フィールド，ユーザーフィールド)の取得と整理
    f = response.text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    iv_list = [int(i) for i in f.split()] #listing initial value
    turn = iv_list[0] 
    length = iv_list[1] 
    width = iv_list[2]
    pointfield = []
    for i in range(length * width):
        pointfield.append(iv_list[i + 3])
    
    return turn,(length,width),pointfield

def _move(port_num,usr,action): # move
    url = 'http://localhost:' + port_num + '/move'
    data = {
        'usr': str(usr),
        'd': num2str_action(action)
    }
    response = requests.post(url, data=data)

def _remove(port_num,usr,action): # remove panel
    url = 'http://localhost:' + port_num + '/remove'
    data = {
        'usr': str(usr),
        'd': num2str_action(action)
    }
    response = requests.post(url, data=data)

def _getField(port_num, length, width): # get point field, user field
    url = 'http://localhost:' + port_num + '/show'
    f = requests.post(url).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    iv_list = [int(i) for i in f.split()]
    uf = []
    for i in range(length):
        l = []
        for j in range(width):
            l.append(iv_list[length* width + width * i + j])
        uf.append(l)
    pf = []
    for i in range(length):
        l = []
        for j in range(width):
            l.append(iv_list[width * i + j])
        pf.append(l)
    return pf,uf

def _calcPoint(port_num): # calculate point
    url = 'http://localhost:' + port_num + '/pointcalc'
    response = requests.post(url).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    iv_list = [int(i) for i in response.split()]
    return iv_list # [tile point 1, field point 1, total point 1, tile point 2, field point 2, total point 2]

def _judgeDirection(port_num,usr,action): # judge direction 
    url = 'http://localhost:' + port_num + '/judgedirection'
    data = {
        'usr': str(usr),
        'd': num2str_action(action)
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

def _changeField(port_num): # change field 
    url = 'http://localhost:' + port_num + '/change'
    f = requests.post(url)

def _getPosition(port_num, usr): # get position
    url = 'http://localhost:' + port_num + '/usrpoint'
    data = {
        'usr': str(usr)
    }
    response = requests.post(url, data=data)
    f = response.text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    pos_array =[int(i) for i in f.split()]
    return pos_array  # [x(column), y(row)]


def num2str_action(action): # convert number into string
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