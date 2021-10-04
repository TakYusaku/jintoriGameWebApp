# Jintori GAME 

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
|    ├── [go file]
|    └── memo.txt
└── web_app
    ├── ai_model
    │   ├── [python souce code of DQNmodel]
    │   └── model_parameter
    │       └── [.pt file]
    ├── [python souce code of webApp]
    ├── static
    │   ├── js
    |       └── [js file]
    └── templates
        └── [html file]
```

* api (directory)  
フィールド情報を取得したり，エージェントを操作するapiを実装したソースコード(python)  
* docker (directory)  
    * go_server(directory)  
    server-field(directory)にあるgo-langファイルを実行できる環境を構築するDockerfile  
    * ubuntu(directory)  
    web_appのための環境を構築するDockerfile  
* server-field(diectory)  
    フィールドを構成するgo-langファイル  

## dockerfile
docker/ubuntu/ にあるDockerfileを使ってください
## docker を立ち上げる時の注意
> docker run -it -d -p 8002:5000 -p 8003:8008 -v [host側の作業ディレクトリ(このjintoriGameのディレクトリ)]:/home/develop --name [image名] [container名] bash  

でrunしてください.

## webappの使い方
1.server-field/jintori-field.go を 'go run jintori-field.go'で実行する  
2.他のターミナルで，web_app/jingame_web.py を 'python3 jingame_web.py' で実行する  
3.'http://localhost:8002/home_page' で使用できる

