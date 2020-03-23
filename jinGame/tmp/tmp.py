
    # 以下，throough_alg_04/agent.py/main() より
def main(df_environ,test=False):
    # DB接続
    print('DYNAMO_TABLE_NAME: '+DYNAMO_TABLE_NAME)
    db_agent = get_dynamo_db_agent(DYNAMO_TABLE_NAME)

    df_price = pd.DataFrame(columns=['itemId', 'newPrice', 'Loss']) # 変更の余地あり (newPrice <=> newPosition, itemID <=> usrID)
    # k_division の取得
    k_divisions = set(df_environ['kDivision'])

    # df_environ,features_list, before_features_list, category_list, states_num の取得
    # dataの内訳は, df_environ(csv)の features_list, before_features_list に当たるデータ(曜日だけone-hot-vector)
    data = load_csv(df_environ,features_list, before_features_list, category_list, states_num)

    for k_division in k_divisions:
        model = param_init_model(data, k_division, states_num, ite = 20, epoch = 5) # 楽観的初期化のため
        # k_divisionsの中から，共通するk_divisionのモデルを取得する
        df_division = df_environ[df_environ['kDivision'] == k_division]
        agent = DQNAgent(k_division)
        item_id_division = df_division['itemId'].values
        # model.state_dict() はネットワークのパラメータを返す
        new_price_division, loss = agent.run_agent(db_agent, df_division, model.state_dict())
        
        df_dic = {'itemId': item_id_division, 'newPrice': new_price_division, 'Loss': np.array([loss] * len(item_id_division))} # 改善の余地あり
        df_price_division = pd.DataFrame(data=df_dic)
        df_price = df_price.append(df_price_division, sort=False)

    df_price.sort_values(by="itemId")
    df_price = df_price.reset_index(drop=True)
    print(df_price)
    df_price.to_csv('./price_history{}.csv'.format(datetime.date.today()), encoding='shift_jis')
    #agentのパラメータをEC2に保存するためにファイル吐き出しを行なっておく
    torch.save(agent.policy_net.state_dict(),'./'+EXPORT_POLICY_FILE_NAME)
    torch.save(agent.target_net.state_dict(),'./'+EXPORT_TARGET_FILE_NAME)

    mime = mimetypes.guess_type('./'+EXPORT_POLICY_FILE_NAME)
    print('MIME TYPE ------------------------------')
    print(mime)
    
    return df_price