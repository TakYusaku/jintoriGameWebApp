#from api_jintori import *
import numpy as np
import pandas as pd
import torch


'''

print(s_judgeDirection('http://localhost:8000',1,6,"m"))
s_move('http://localhost:8000',*[1,5])

ds = []
a = {"ac":1,"di":3}
ds.append(a)
b = {"ac":2,"di":4}
ds.append(b)

print(ds[0]["ac"])

#s_move('http://localhost:8000',1,7)

pos = s_getPosition('http://localhost:8000',2)
pf,uf= s_getField('http://localhost:8000',10,10)

def get_dim_list(li):
    return [len(li),len([len(v) for v in li])]

def get_around_point(pf,x,y): # x,y は座標
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

print(get_around_point(pf,*pos))

p_list =s_calcPoint('http://localhost:8000')
idx = 3
print(p_list)
point = p_list[idx:idx+3]
print(point)

p = [1,2,3]
d = [2,3,2]

ss = [p,d]
print(ss)
ss[0] = d
ss[1] = p
print(ss)

dtype = torch.float
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print("device:", device)

a = [[1],[2],[2],[2],[3]]
df = pd.DataFrame(a,
                  columns=['col_0'],
                  index=['row_0','row_1','row_2','row_3','row_4'])

#print(df['col_0'].values)
#print(df[df['col_0'].values==2])
#print(np.array([1,2]))
data_tch = torch.from_numpy(np.array(a)).float()
bb = torch.cat(
    (data_tch, data_tch),
    dim = 1
)
#print(bb)
data = torch.cat(
    (bb, bb),
    dim = 0
)
#print(data.to(device))

b = [[1,2],[3,4],[5,6]]
#df_b = pd.DataFrame(b,
#                  columns=['col_0','col_1'],
#                  index=['row_0','row_1','row_2'])
df_b = pd.DataFrame(b)
data_tch_1 = torch.from_numpy(df_b.values).float()
data = torch.cat(
    (data_tch_1, data_tch_1),
    dim = 0
)
#print(data)
#print(len(data))

c = [1,2,3,4,5,6]
df_c = pd.DataFrame([c])
dataa = torch.from_numpy(np.array(df_c)).float()
#print(dataa.shape)
datab = torch.cat(
    (dataa, dataa+1),
    dim = 0
)
#print(datab)
#print(datab.shape)

datac = torch.cat(
    (datab,datab*2),
    dim = 1
)
#print(datac)
datab=datac
print(datab.shape[0])
print(datab)
state = torch.FloatTensor(datab[:,6:])
print(state)
#print(df['col_0'].values == np.array([1,2]))

df_action = {}
df_action["is_possible"] = []
df_action["is_possible"].append('1')
df_action["is_possible"].append('2')
print(df_action)
print(np.array([True]*2))


df_dic = {'calcAction': np.array([1,2]), 'Loss': np.array([0.1]*2), 'reward': np.array([2,4])}#* len(item_id_division))}
df_dic["steps_done"] = np.array([5]*2)

import pandas as pd
df = pd.DataFrame(df_dic)
print(df)
print(np.empty(0))
'''
file_name = 'test_binary'
import pickle
lst = [[2,3,4],[11,12,13]]
data = {'lst':lst, 'name':'sss'}
with open(file_name,'wb') as f:
    f.write(pickle.dumps(data))
'''
with open(file_name, 'rb') as f:
    data = pickle.loads(f.read())

print(data['lst'])
'''
datas = {'lst':[2,2,3], 'name':'aaa','updat':5}
with open(file_name,'wb') as f:
    f.write(pickle.dumps(datas))

with open(file_name, 'rb') as f:
    data = pickle.loads(f.read())
print(data)

'''
file_names = 'test_binary_2'
try:
    with open(file_names, 'rb') as f:
        lst = pickle.loads(f.read())
except:
    print("noen")

with open(file_names,'wb') as f:
    f.write(pickle.dumps([]))
try:
    with open(file_names, 'rb') as f:
        lst = pickle.loads(f.read())
except:
    print("noen")
'''