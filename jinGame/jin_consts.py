# -*- coding: utf-8 -*-
from jin_util import *
import os

date_today_str = get_japantime_today()
TODAYS_DATE = date_today_str
TODAYS_DATE_DIRECTORY_NAME = date_today_str + '/'


LOG_DIRECTORY_NAME = './log/'
EVAL_HISTORY_DIRECTORY_NAME = './save/history/eval/' + TODAYS_DATE_DIRECTORY_NAME
os.makedirs(EVAL_HISTORY_DIRECTORY_NAME, exist_ok=True)
LEARN_HISTORY_DIRECTORY_NAME = './save/history/learn/' + TODAYS_DATE_DIRECTORY_NAME
os.makedirs(LEARN_HISTORY_DIRECTORY_NAME, exist_ok=True)
PARAMETER_DIRECTORY_NAME = './save/parameter/' + TODAYS_DATE_DIRECTORY_NAME
os.makedirs(PARAMETER_DIRECTORY_NAME, exist_ok=True)
REPLAYMEMORY_DIRECTORY_NAME = './save/replay_memory/'


# EXPORT_EVAL_HISTORY_FILE_NAME = ''
# eval_history_(現在のセット数(現在何セット目か))_(現在のゲーム回数(現在selfplayの何ゲーム目か))_(TODAYS_DATE).csv
# EXPORT_LEARN_HISTORY_FILE_NAME = ''
# learn_history_(現在のセット数(現在何セット目か))_(現在のepoch回数(現在selfplayの何ゲーム目か))_(TODAYS_DATE).csv

IMPORT_FILE_NAME='environment_10_request.csv'
EXPORT_FILE_NAME='environment_10_response.csv'

IMPORT_POLICY_FILE_NAME=''
IMPORT_TARGET_FILE_NAME = ''
EXPORT_POLICY_FILE_NAME = ''
EXPORT_TARGET_FILE_NAME = ''
'''
EXPORT_REPLAYMEMORY_FILE_NAME_1 = ''
EXPORT_REPLAYMEMORY_FILE_NAME_2 = ''
IMPORT_REPLAYMEMORY_FILE_NAME_1 = ''
IMPORT_REPLAYMEMORY_FILE_NAME_2 = ''
'''

'''
.
├── jinGame.py
├── jin_agent.py
├── jin_consts.py
├── jin_execute.py
├── jin_init_parameter_optim.py
├── jin_replayMemory.py
├── jin_util.py
├── log (directory)
├── save
│   ├── history (directory)
│   ├── parameter (directory)
│   └── replay_memory (directory)
------ 無視 ------
└── tmp (directory)
    ├── test.py
    ├── test_csv.csv
    ├── text.txt
    └── tmp.py
'''