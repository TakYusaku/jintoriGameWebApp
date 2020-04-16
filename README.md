# Jintori GAME 
unfinished...
## directory structure
```
.
├── README.md
├── api
│   └── [source code (python)]
├── docker
│   ├── memo.txt
│   └── ubuntu
│       └── [Dockerfile]
├── rule-jintori.txt
└── server-field
    ├── [go file]
    └── memo.txt
```

* api (directory)  
フィールド情報を取得したり，エージェントを操作するapiを実装したソースコード(python)  
* docker (directory)  
    * go_server(directory)  
    server-field(directory)にあるgo-langファイルを実行できる環境を構築するDockerfile  
    * ubuntu(directory)  
    エージェントの学習のための環境を構築するDockerfile  
* jinGame(directory)  
エージェントを学習させるソースコードと，logデータを保存するdirectory  
    * log(directory)  
    学習開始時刻と終了時刻を記録する  
    * save(directory)  
    学習のログ，ネットワークパラメータ，replaymemoryの保存  
        * history(directory)  
        学習時(learn)と評価時(eval)のログを保存する  
        * parameter(directory)  
        ネットワークパラメータの保存  
        * replay_memory(directory)  
        replay memoryのバイナリデータ
* server-field(diectory)  
    フィールドを構成するgo-langファイル  

## dockerfile
webapp も DQN学習　のも，docker/ubuntu/ にあるDockerfileを使ってください
## docker を立ち上げる時の注意
> docker run -it -d -p 8002:5000 -p 8003:8008 -v [host側の作業ディレクトリ(このjintoriGameのディレクトリ)]:/home/develop --name [image名] [container名] bash  

でrunしてください.

## webappの使い方
1.server-field/jintori-field_copied.go を 'go run jintori-field_copied.go'で実行する  
2.他のターミナルで，web_app/jingame_web.py を 'python3 jingame_web.py' で実行する  
3.'http://localhost:8002/home_page'で使用できる

## jinGameのソースコードについて  
* jin_NN.py  
ネットワークの構成  
* jin_agent.py  
学習，評価に関する処理を記述したソース  
* jin_consts.py  
データ・ログの保存先を記したファイル  
* jin_execute.py  
学習・評価を実行する  
* jin_init_parameter_optim.py  
楽観的初期化のためのソース  
* jin_jinGame.py  
陣取りゲームを行うために必要な機能集  
* jin_parameter.py    
Epoch, Evaluation, Set 数を記したファイル  
* jin_replayMemory.py  
replay memory を構成するソース  
* jin_util.py  
現在時刻等を取得し，変換するソース

## 'save' directory の中身について
