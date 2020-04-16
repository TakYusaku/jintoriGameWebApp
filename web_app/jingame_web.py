import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api_jintori

from flask import Flask, render_template, request, jsonify
import json
app = Flask(__name__)

from jingame_core_src import *

## global variable
width = 0
length = 0
domain = 'http://localhost:8008' # field serverのアドレス


############ ここから本番 #############
web_jinGame_env = web_jinGame(domain)

# ホーム画面
@app.route('/home_page')
def home():
    return render_template('home_page.html')

#### vs ai ####
# プレイ画面
@app.route('/play_page_vs_ai')
def play_page():
    global web_jinGame_env
    web_jinGame_env._web_init()

    return render_template('play_page_vs_ai.html')

# game start
@app.route('/play_page_vs_ai/game_start',  methods=["GET", "POST"])
def game_start():
    global web_jinGame_env
    data = web_jinGame_env._start_game()
    print(data)
    return jsonify(data)

# game action
@app.route('/play_page_vs_ai/game_action', methods=["GET", "POST"])
def game_action():
    respond = request.json
    global web_jinGame_env
    res, data = web_jinGame_env._process(respond)
    return jsonify(data)

#### vs human ####
# プレイ画面
@app.route('/play_page_vs_human')
def play_page_vs_human():
    global web_jinGame_env
    web_jinGame_env._web_init()

    return render_template('play_page_vs_human.html')

# game start
@app.route('/play_page_vs_human/game_start',  methods=["GET", "POST"])
def game_start_vs_human():
    global web_jinGame_env
    data = web_jinGame_env._start_game()
    print(data)
    return jsonify(data)

# game action
@app.route('/play_page_vs_human/game_action', methods=["GET", "POST"])
def game_action_vs_human():
    respond = request.json
    global web_jinGame_env
    res, data = web_jinGame_env._process_human(respond)
    return jsonify(data)
'''
# game restart
@app.route('/play_page/restart', methods=["GET", "POST"])
def restart():
'''



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)