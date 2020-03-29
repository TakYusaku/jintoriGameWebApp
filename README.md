# Jintori GAME

## directory structure
```
.
├── README.md
├── api
│   └── [source code (python)]
├── docker
│   ├── go_server
│   │   └── [Dockerfile]
│   ├── memo.txt
│   └── ubuntu
│       └── [Dockerfile]
├── jinGame
│   ├── [source code (python)]
│   ├── log
│   ├── save
│   │   ├── history
│   │   │   ├── eval
│   │   │   │   ├── [csv file]
│   │   │   └── learn
│   │   │       └── [csv file]
│   │   ├── parameter
│   │   │   └── [date(directory)]
│   │   │       └── [pt file (network parameter)]
│   │   └── replay_memory
│   │       └── [binary file]
│   └── tmp
├── other
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