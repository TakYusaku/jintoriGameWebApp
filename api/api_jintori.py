import requests
import random


def s_start(domain): # game start
    url = domain + '/start'
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

def s_move(domain,usr,action): # move
    url = domain + '/move'
    data = {
        'usr': str(usr),
        'd': num2str_action(action)
    }
    response = requests.post(url, data=data)

def s_remove(domain,usr,action): # remove panel
    url = domain + '/remove'
    data = {
        'usr': str(usr),
        'd': num2str_action(action)
    }
    response = requests.post(url, data=data)

def s_getField(domain, length, width): # get point field, user field
    url = domain + '/show'
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

def s_calcPoint(domain): # calculate point
    url = domain + '/pointcalc'
    response = requests.post(url).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    iv_list = [int(i) for i in response.split()]
    return iv_list # [tile point 1, field point 1, total point 1, tile point 2, field point 2, total point 2]

def s_judgeDirection(domain,usr,action): # judge direction
    url = domain + '/judgedirection'
    flg, motion = num2str_motion(action)
    if flg:
        d = action
    else:
        if action < 13:
            d = action - 9
        else:
            d = action - 8
    data = {
        'usr': str(usr),
        'd': num2str_action(d),
        'motion': motion
    }

    f = requests.post(url, data = data).text.encode('utf-8').decode().replace("\n", " ").replace("  "," ")
    iv_list = [i for i in f.split()]

    pos = s_getPosition(domain, usr)
    idx = next_pos_idx(d)
    next_pos = [pos[0]-idx[0],pos[1]-idx[1]]

    if action==4:
        return "5", data, next_pos

    if iv_list[0] == "Error": # out of field
        return "1", data, next_pos
    elif iv_list[0] == "is_panel": # is pannel
        return "3", data, next_pos
    elif iv_list[0] == "is_user": # is user
        return "4", data, next_pos
    elif iv_list[0] == "no_panel": # no panel
        return "2", data, next_pos
    else:
        return "5", data, next_pos # no plobrem


def s_changeField(domain): # change field 
    url = domain + '/change'
    f = requests.post(url)

def s_getPosition(domain, usr): # get position
    url = domain + '/usrpoint'
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

def next_pos_idx(dire):
    if dire == 0:
        return [1,1]
    elif dire == 1:
        return [0,1]
    elif dire == 2:
        return [-1,1]
    elif dire == 3:
        return [1,0]
    elif dire == 4:
        return [0,0]
    elif dire == 5:
        return [-1,0]
    elif dire == 6:
        return [1,-1]
    elif dire == 7:
        return [0,-1]
    elif dire == 8:
        return [-1,-1]   



def num2str_motion(action):
    if action < 9:
        return True, "move"
    else:
        return False, "remove"