# https://qiita.com/uji_/items/8c9eda89526abe0ba900 より
# 2020/03/07(Sat) 作成

FROM golang:latest
# コンテナ内に作業ディレクトリを作成
RUN mkdir /go/src/work
# コンテナログイン時のディレクトリ指定
WORKDIR /go/src/work
# ホストのファイルをコンテナの作業ディレクトリに移行
ADD ./work/ /go/src/work
# port
EXPOSE 8000