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
domain = 'http://localhost:8008'



# home
@app.route('/home')
def hello():
    turn,(length,width),pointfield = api_jintori.s_start('http://localhost:8000')
    return str(pointfield)

# play page
@app.route('/play', methods=["GET", "POST"])
def playGame():
    title = 'jinGame'
    return title

# move
@app.route('/play/move', methods=["GET", "POST"])
def move():
    # 移動したい位置を取得(pos)し，
    respond = json.loads(request.form['text'])
    res, code = is_right_(domain, respond)
    if res:
        tmp = 'ok'
        show()
    else:
        if code==1:
            tmp = 'nos'
            return tmp
        else:
            tmp = 'no'
            return tmp

# move
@app.route('/move', methods=["GET", "POST"])
def move_ajx():
    #移動したい位置を取得(pos)し，
    respond = request.json
    print(respond)
    global width, length, domain
    res, code = is_right_(domain, respond)
    pf ,uf = api_jintori.s_getField(domain, length, width)
    data = {
        'is_right':res,
        'code':code,
        'pf':pf,
        'uf':uf
    }
    #data = get_send_data(domain, length, width)
    return jsonify(data)


@app.route("/index")
def index():
    turn,(s_length,s_width),pointfield = api_jintori.s_start(domain)
    pf_reshape = []
    global width, length
    width = s_width
    length = s_length
    pf ,uf = api_jintori.s_getField(domain, length, width)
    return render_template('index.html', pf=pf, uf=uf)

@app.route("/show")
def show():
    global width, length
    pf ,uf = api_jintori.s_getField(domain, length, width)
    return render_template('index.html', pf=pf, uf=uf)

@app.route("/field")
def field():
    '''
    global width, length
    pf ,uf = api_jintori.s_getField(domain, length, width)
    '''
    turn,(s_length,s_width),pointfield = api_jintori.s_start(domain)
    pf_reshape = []
    global width, length
    width = s_width
    length = s_length
    pf ,uf = api_jintori.s_getField(domain, length, width)
    data = {
        'pf':pf,
        'uf':uf
    }
    print(data)
    return jsonify(data)

@app.route('/test')
def test():
    return render_template('index_1.html')

############ ここから本番 #############
web_jinGame_env = web_jinGame(domain)

# ホーム画面
@app.route('/home_page')
def home():
    return render_template('home_page.html')

# プレイ画面
@app.route('/play_page')
def play_page():
    global web_jinGame_env
    web_jinGame_env._web_init()

    return render_template('play_page.html')

# game start
@app.route('/play_page/game_start',  methods=["GET", "POST"])
def game_start():
    global web_jinGame_env
    data = web_jinGame_env._start_game()
    print(data)
    return jsonify(data)

# game action
@app.route('/play_page/game_action', methods=["GET", "POST"])
def game_action():
    respond = request.json
    global web_jinGame_env
    res, data = web_jinGame_env._process(respond)
    return jsonify(data)

'''
# game restart
@app.route('/play_page/restart', methods=["GET", "POST"])
def restart():
'''



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)