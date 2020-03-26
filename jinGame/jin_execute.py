# -*- coding: utf-8 -*-

import sys
import os
import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from jin_agent, jin_util import *

file_path = os.path.dirname(os.path.abspath(__file__))

def main(file_path):
    '''
    #################################################################
    # 日付判定

    if nextExecutedAt is None:
        nextExecutedAt = get_japantime_today()
    print('nextExecutedAt:',nextExecutedAt)
    #################################################################
    '''
    TODAYS_DATE = date_to_date(get_japantime_now())
    fn = LOG_DIRECTORY_NAME + 'exec_log_at_' + TODAYS_DATE + '.txt'
    #try:
        message = 'start time at:' + TODAYS_DATE + '\n'
        f = open(fn,'a')
        f.write(message)
        f.close()

        agent.main() # 学習諸々の実行

        now_time = date_to_date(get_japantime_now())
        message = '(s)finished time at:' + now_time + '\n'
        f = open(fn,'a')
        f.write(message)
        f.close()        
    '''
    except :
        import requests
        import json
        import traceback
        
        now_time_str = date_to_date(get_japantime_now())
        message = now_time_str + "_an error has occurred...：" + traceback.format_exc() # エラーを文字列に変換
        # textファイルに書き出す
        f = open(fn,'a')
        f.write(message)
        f.close()

        raise

    return True
    '''

if __name__ == '__main__':
    '''
    args = sys.argv
    if len(args) > 1:
        print('args exist')
        print(str(args))
        nextExecutedAt = str(args[1]).split('/')[0]
    else:
        nextExecutedAt=None
    '''
    print('start execute')
    main(file_path)
    print('done execute')