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

> api  
フィールド情報を取得したり，エージェントを操作するapiを実装したソースコード(python)  
