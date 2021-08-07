FROM lambci/lambda:build-python3.8

WORKDIR /srv
ENV CHROMEDRIVER_PATH='/usr/local/bin/'

COPY requirements.txt ./requirements.txt

# リポジトリを追加
COPY google-chrome.repo /etc/yum.repos.d/google-chrome.repo

RUN yum update -y

# install Chrome
RUN yum install -y google-chrome-stable

# install ChromeDriver
# 何故かchromedriver-binaryでインストール出来ないので直接インストール
RUN wget https://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver $CHROMEDRIVER_PATH && \
    rm chromedriver_linux64.zip

# install lib
# GConf2がなくてchromedriverが動かないのでインストール。詳細はreadmeに記載
RUN yum install -y GConf2

RUN pip install -r requirements.txt --upgrade
