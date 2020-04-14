# last update : 2020/03/26(Thu)
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y
#RUN apt install -y python2.7-dev python3.6-dev pylint
RUN apt install -y python3.7
#RUN apt install -y python-dev python-pip python-setuptools \ 
RUN apt install -y python3-pip python3-setuptools python-pip
# tkinter
RUN apt install -y python3-tk

# other tools
RUN apt install -y curl
RUN apt install -y nano
RUN apt install -y git
RUN apt install -y golang

RUN apt clean -y
RUN apt autoremove -y
RUN apt update -y
RUN apt upgrade -y
RUN apt autoremove -y
RUN apt autoclean -y

RUN pip3 install retry && pip3 install pandas && pip3 install collections-extended && pip3 install requests && pip3 install flask
RUN pip install pytz && pip install python-dateutil
RUN pip3 install torch==1.3.0+cpu torchvision==0.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# mount volume
RUN mkdir /home/develop
VOLUME /home/develop

EXPOSE 8000

CMD echo 'successful'