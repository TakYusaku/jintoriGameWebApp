from jinGame import jinGAME
import numpy as np
import torch
import pandas as pd
import deque
import datetime

class jinGame_DQNAgent(DQNAgent):
    # 何か初期化がいるなら追加する
    def __init__(self,k_division, states_number=states_num, eps_start=0.99, eps_end=0.1, eps_decay=100,gamma=0.9, target_update=7):
        super(jinGame_DQNAgent,self).__init__(k_division, states_number, eps_start, eps_end, eps_decay, gamma, target_update)
        self.action_history = deque() # 行った行動を保存しておく

    def check_action(self,action):
        # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
        if action["n_position"][0] == action["n_position"][1]: # 行動先がかぶるとき
                return False
        else:
            return True

    def adjust_data(self, action):
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

    def do_action(self, env,m_data):
        for i in range(2):
            if m_data[i]['motion'] == "move":
                env._move(*m_data[i]['lists'])
            elif m_data[i]['motion'] == "remove":
                env._remove(*m_data[i]['lists'])

    def get_dim_list(self, li):
        return [len(li),len([len(v) for v in li])]

    def get_around_point(self, pf,x,y): # x,y は座標
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

    def get_features(self, env,turn,usr):
        data = []
        if turn == 0:
            data = [0] * 18
        else:
            a_pos_list = env._getPosition(usr)
            a_pos = wid*(a_pos_list[1]) + a_pos_list[0] # 味方位置をナンバリング (0~width*length-1)
            if usr==1:
                b_usr = 2
                idx = 0
            else:
                b_usr = 1
                idx = 3
            b_pos_list = env._getPosition(b_usr)
            b_pos = wid*(b_pos_list[1]) + b_pos_list[0] # 相手位置をナンバリング (0~width*length-1)

            data = [env.turn, turn, env.length, env.width, a_pos, b_pos] # len(data) = 6

            pf,uf = env._getField()
            around_point = get_around_point(pf,*a_pos_list) # 周辺のポイント
            data.extend(around_point) # len(data) = 6 + 9 = 15
            #b_around_point = get_around_point(pf,*b_pos_list)
            p_list = env._calcPoint()
            point = p_list[idx:idx+3] # 自分のポイント
            data.extend(point) # len(data) = 15+3 = 18

        df_data = pd.DataFrame([data])
        data_tch = torch.from_numpy(np.array(df_data)).float()
        return data_tch

    def _load_agent(self, fn_agent): # fn_agent = {"policy": [name], "target": [name] }
        IMPORT_POLICY_FILE_NAME = fn_agent["policy"]
        IMPORT_TARGET_FILE_NAME = fn_agent["target"]
        self.policy_net.load_state_dict(torch.load("./save/parameter/" + IMPORT_POLICY_FILE_NAME))
        self.target_net.load_state_dict(torch.load("./save/parameter/" + IMPORT_TARGET_FILE_NAME))

    def _select_row_by_userID(self,fn_agent, userID):
        # replay_memoryのデータを取得
        # replay_memory_memory = :replay_memory_memory, steps_done = :steps_done
        # result = db_agent.get_item(Key={'k_division': k_division, 'item_id': item_id})
        # 上のやつを参考にデータを取得
        try:
            row = result
        except:
            print("not found memory by userID")
            row = None
        finally:
            return row

    def reward(self,reward_r):
        return 2*sigmoid(reward_r/100)-1

    def _insert_agent(self, file_name,user_id):
        japantime_now = get_japantime_now()
        japantime_now_str = date_to_date(japantime_now)
        #最初の保存でのデータは使えないので、pickled_replay_memory_itemID_valueListに[]を格納する
        pickled_replay_memory_itemID_valueList = pickle.dumps([])
        #insert_dictはdynamo_insert_itemメソッドで変数Itemに格納されている。
        insert_dict = {
            'item_id': int(user_id),
            'steps_done': int(self.steps_done),
            'replay_memory_memory': pickled_replay_memory_itemID_valueList,
            'create': japantime_now_str
        }

        print('steps_done: ', self.steps_done)
        print('create: ', japantime_now_str)
        print('insert agent: done')
        file_name = file_name + '_usr' + str(user_id)
        self._save_data_pickle(file_name, insert_dict)
        return True

    def _save_data_pickle(self,file_name,data):    
        file_name = './replay_memory/' + file_name 
        with open(file_name,'wb') as f:
            f.write(pickle.dumps(data))
        return True

    def _read_data_pickle(self,file_name,userID=None):
        if userID is not None:
            file_name = file_name + '_usr' + str(userID)
        try:
            with open(file_name, 'rb') as f:
                data = pickle.loads(f.read())
            return data
        except:
            return None

    def _save_agent(self, file_name, userID, replay_memory_userID_valueList):
        japantime_now = get_japantime_now()
        japantime_now_str = date_to_date(japantime_now)
    
        pickled_replay_memory_itemID_valueList = pickle.dumps(replay_memory_itemID_valueList)
        
        update_dict = {
            'item_id': int(userID),
            'steps_done': int(self.steps_done),
            'replay_memory_memory': pickled_replay_memory_itemID_valueList
            'updated': japantime_now_str
        }
        file_name = file_name + '_usr' + str(userID)
        self._save_data_pickle(file_name,update_dict)
        print('saved agent: done')
        return True

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

    def _run_agent(self, fn_agent, df_division, model_state_dict):
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
        self._init_agent()
        #初回はpytorchのパラメータ保存ファイルがないので、loadしない。初回はsteps_done=0となる。
        if self.steps_done==0:
        #ここで楽観的初期化を行う
            self.policy_net.load_state_dict(model_state_dict)
            self.target_net.load_state_dict(model_state_dict)
        if self.steps_done != 0:
            self._load_agent(fn_agent)

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
            row = self._read_data_pickle(*[fn_agent["replay_memory"],userID])
            if row is None:
                none_user_id_list.append(userID)
                replay_memory_dic[userID-1] = None
            else:                
                replay_memory_dic[userID-1] = pickle.loads(row['replay_memory_memory'])


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

            replay_memory_itemID_valueList = replay_memory_dic[userIDList[i]-1]
            #追加するvalue
            #addValue = [state[i], actionList[i], next_state[i], reward[i],itemIDList[i]]
            addValue = [state[i], actionList[i], next_state[i], reward[i], userIDList[i]]
            #continueでない時、２回目以降などにくる。
            #valueListにappendする
            replay_memory_itemID_valueList.append(addValue)
            #更新したvalueListを格納する。
            #replay_memory_dic[itemIDList[i]] = replay_memory_itemID_valueList
            replay_memory_dic[userIDList[i]-1] = replay_memory_itemID_valueList
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
        self.steps_done += 1

        for userID in enumerate(userIDList):
            if userID in none_user_id_list: # row is None.
                self._insert_agent(fn_agent['row'], userID)
            '''
            elif userID in not_max_steps_done_user_id_list:
                print("IN not_max_steps_done_user_id_list")
                replay_memory_userID_valueList = []
                self._save_replay_memory(fn_agent,itemID,replay_memory_itemID_valueList,logNewPrice)
            '''
            else: # no plobrem
                replay_memory_itemID_valueList = replay_memory_dic[userID-1]
                self._save_agent(fn_agent['row'],userID,replay_memory_itemID_valueList)

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
        return new_action, returnLoss, np.array(reward)


    def agent_learning(self, env,fn_agent,epochs, idx):
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


            for epc in range(epochs):
                # game start
                turn, length, width = env._start()
                before_features = []
                # turn の数だけ，行動を行う
                for t in turn:
                    if t == 0: # before_feature の初期化
                        before_features = torch.cat(
                            (get_features(t,1),get_features(t,2)),
                            dim = 0
                        )
                    else: # フィールドの得点を変える
                        env._changeField()

                    # 2エージェント分の特徴量をまとめる
                    now_features = torch.cat(
                        (get_features(env,t+1,1),get_features(env,t+1,2)),
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
                    k_division = 17 # 行動数
                    states_num = 18 #len(data) 特徴量の大きさ(skalar)
                    model = param_init_model(data, k_division, states_num, ite = 20, epoch = 5)

                    # 特徴量をもとにネットワークから行動を取得
                        # run_agent() で次の行動を決める(実際に行動はしない)
                    agent = DQNAgent(k_division)
                    # db_agent, df_division
                    new_action, loss, reward = agent.run_agent(fn_agent, df_division, model.state_dict()) # new_action は数字を返す
                    # item_id_division:usrID(のリスト), new_price_division: usrの次の行動("n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード)
                    usr_id_division = np.array([1,2])
                    df_dic = {'usrID': usr_id_division, 'calcAction': new_action, 'Loss': np.array([loss]*2), 'reward': reward}#* len(item_id_division))}
                    #df_dic = {'calcAction': new_action, 'Loss': np.array([loss]*2), 'reward': reward}#* len(item_id_division))}

                    df_dic = pd.DataFrame(data=df_dic)
                    df_runLog = df_runLog.append(df_dic, sort=False)

                    # action = {"n_position": 座標,"motion": move or remove,"direction": 方向,"is_possible": s_judjedirection()のコード}
                    df_action = {}
                    df_action["is_possible"] = []
                    df_action["motion"] = []
                    df_action["direction"] = []
                    df_action["n_position"] = []

                    for usrID in enumerate(usr_id_division):
                        code, data, next_pos = env._judgeDirection(usrID,new_action[usrID-1])
                        df_action["is_possible"].append(code)
                        df_action["motion"].append(data['motion'])
                        df_action["direction"].append(data['direction'])
                        df_action["n_position"].append(next_pos)
                
                    # エージェントの移動先が重なってるか，いないかを判定
                    cnf = self.check_action(df_action)
                    if cnf: #bool, 重なっていない
                        m_data = self.adjust_data(df_action)
                    else: # 重なっている
                        usr1_data = {'motion':"move", "lists": [1,4]}
                        usr2_data = {'motion':"move", "lists": [2,4]}
                        m_data = [usr1_data,usr2_data]

                    df_dic["is_possible"] = np.array([int(i) for i in enumerate(df_action["is_possible"])])
                    df_dic["is_confliction"] = np.array([cnf]*2)
                    df_dic["steps_done"] = np.array([self.steps_done]*2)

                    # logを保存
                    df = pd.DataFrame(df_dic)
                    df.to_csv('./save/history/history_{}.csv'.format(datetime.date.today()), encoding='shift_jis')
                    
                    
                    # 移動前に得点を取得
                    point_before_moving = env._calcPoint()
                    # 判定後に実際に移動させる
                    do_action(env, m_data)
                    # 行動を保存しておく
                    self.action_history.append(m_data)  

                    ##### ------- #####    
                    # 移動後の得点を取得
                    point_after_moving = env._calcPoint()
                    # 移動後の位置を取得
                    position_after_moving = {'usr1': env._getPosition(1), 'usr2': env._getPosition(2)}
                    # replay_memory により学習させる
                
                    if t+1 == turn:
                        loss_per_epoch.append(loss)
                epochs_done += 1

            fn = self._save_network(fn)
            logs = {"interval": str(idx),"epochs_done": str(epochs_done), "loss_per_epoch": loss_per_epoch, "plicynet_filename":fn["policy"], "target":fn["target"]}

            return True, logs

        except:
            fn = self._save_network(fn)
            logs = {"interval": str(idx),"epochs_done": str(epochs_done), "loss_per_epoch": loss_per_epoch, "plicynet_filename":fn["policy"], "target":fn["target"]}
            return False, logs

    def get_network_fn(self, idx, flag):
        date_today = get_japantime_today()
        date_today_str = date_to_str(date_today)
        date_now = get_japantime_now() # util.py
        date_now_str = date_to_date(date_now)
        idx_str = str(idx)
        if flag:
            flag_str = 'T'
        else:
            flag_str = 'F'
        tmp = date_today_str + '/' + date_now_str + '_' + idx_str + '_' + flag_str
        fn = {"policy":'policy_' + tmp, "target": 'target_' + tmp}
        return fn

    def _save_network(self, idx, flag):
        fn = self.get_network_fn(idx, flag)
        EXPORT_POLICY_FILE_NAME = fn["policy"]
        EXPORT_TARGET_FILE_NAME = fn["target"]
        torch.save(agent.policy_net.state_dict(),'./save/parameter/'+EXPORT_POLICY_FILE_NAME)
        torch.save(agent.target_net.state_dict(),'./save/parameter/'+EXPORT_TARGET_FILE_NAME)
        return fn

    def agent_evaluation(self):
        try:
            return True
        except:
            return False
    
    def select_model(self):


    def process(self, env, fn_agent, epochs, interval):
        for idx in range(interval):
            result, a_logs = self.agent_learning(env, fn_agent, epochs, idx)
            if not result:
                return a_logs
            opponent = self.select_model()
            result, e_logs = self.agent_evaluation(agent, opponent)
            if not result:
                return logs
            





def main():
    fn_agent = {"policy": '[name]', "target": '[name]' , "row": '[name]', "replay_memory":} # path

if __name__ == "__main__":
    g_env = jinGAME(8000)
