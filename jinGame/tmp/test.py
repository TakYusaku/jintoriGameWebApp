features_list = ['dailyPrice', 'threeDaysPrice', 'weeklyPrice', 'dayOfTheWeek',
                 'discount','dailySales', 'threeDaysSales', 'weeklySales', 'dailyRevenue', 'threeDaysRevenue',
                 'weeklyRevenue', 'categoryId', 'dailyBuyers', 'threeDaysBuyers', 'weeklyBuyers', 'dailyUv',
                 'threeDaysUv', 'weeklyUv', 'dailyPv', 'threeDaysPv', 'weeklyPv', 'rate', "isSaleDay"]

before_features_list = ['beforeDailyPrice', 'beforeThreeDaysPrice', 'beforeWeeklyPrice', 'beforeDayOfTheWeek',
                 'beforeDiscount','beforeDailySales', 'beforeThreeDaysSales', 'beforeWeeklySales', 'beforeDailyRevenue', 'beforeThreeDaysRevenue',
                 'beforeWeeklyRevenue', 'categoryId', 'beforeDailyBuyers', 'beforeThreeDaysBuyers', 'beforeWeeklyBuyers', 'beforeDailyUv',
                 'beforeThreeDaysUv', 'beforeWeeklyUv', 'beforeDailyPv', 'beforeThreeDaysPv', 'beforeWeeklyPv', 'beforeRate', "beforeIsSaleDay"]

#楽天 + yahoo
category_list = ['レディースファッション', 'メンズファッション', '腕時計、アクセサリー', '食品',
                 'ドリンク、お酒', '家電', 'スマホ、タブレット、パソコン', 'テレビ、オーディオ、カメラ', '家具、インテリア',
                 'キッチン、日用品、文具', 'スポーツ', 'アウトドア、釣り、旅行用品', 'コスメ、美容、ヘアケア', 'ダイエット、健康',
                 'ペット用品、生き物', '花、ガーデニング', 'DIY、工具', '自動車', 'バイク', '自転車', 'ベビー、キッズ、マタニティ',
                 'ゲーム、おもちゃ', '楽器、手芸、コレクション', 'CD、音楽ソフト', 'DVD、映像ソフト', '本、雑誌、コミック',
                 'レンタル', 'リフォーム', 'サービスクーポン、引換券', '各種サービス','カタログギフト・チケット','デジタルコンテンツ',
                 'バッグ・小物・ブランド雑貨','医薬品・コンタクト・介護','靴','光回線・モバイル通信','住宅・不動産']


# To be encoded as one-hot vector
day_of_the_week_idx = features_list.index('dayOfTheWeek')
day_of_the_week_len = 7

#indexメソッド 引数に調べたい値を指定すると0始まりのインデックスが取得
category_id_idx = features_list.index('categoryId')
category_id_len = len(category_list)
#day_of_the_week と category_idがonehotに変換される
onehot_idx_list = [day_of_the_week_idx, category_id_idx]
onehot_len_list = [day_of_the_week_len, category_id_len]

print(onehot_idx_list)
print(onehot_len_list)


"""
df_next = environ_df[features_list]
df_before = environ_df[before_features_list]

df_next = torch.from_numpy(df_next.values).float()
df_next = encode_onehot(df_next, onehot_idx_list, onehot_len_list)
df_next = normalize_mask(df_next, onehot_idx_list, onehot_len_list)

df_before = torch.from_numpy(df_before.values).float()
df_before = encode_onehot(df_before, onehot_idx_list, onehot_len_list)
df_before = normalize_mask(df_before, onehot_idx_list, onehot_len_list)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#sys.path.append('../throough_alg_04/src/')
from behaviour import *
from import_csv import *
from util import get_japantime_today

nextExecutedAt = get_japantime_today()
print('nextExecutedAt:',nextExecutedAt)
df_environment = import_csv.main(nextExecutedAt)
df_behaviour = behaviour.Behaviour(df_environment).main(nextExecutedAt)
print(df_behaviour)
print(df_environment)