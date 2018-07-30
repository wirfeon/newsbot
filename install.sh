#!/bin/bash

#set -v

P=/www/newsbot
S=$PWD
SERVICE_NAME=bot.news

rm -f /tmp/$SERVICE_NAME

[ ! -e $P ] && sudo mkdir -p $P

diff -q $P/bot.py bot.py > /dev/null 2>&1 || sudo cp bot.py $P/
diff -q $P/Pipfile Pipfile > /dev/null 2>&1 || (sudo cp Pipfile $P/ && echo 1 > /tmp/$SERVICE_NAME)

if [ ! -e $P/Pipfile.lock ]; then
    echo 1 > /tmp/$SERVICE_NAME
fi

if [ -e /tmp/$SERVICE_NAME ] && [ `cat /tmp/$SERVICE_NAME` == 1 ]; then
    cd $P
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv install --three
    sudo env PIPENV_VENV_IN_PROJECT=1 pipenv update
    cd $S
fi

rm -f /tmp/$SERVICE_NAME

if [ ! -e /etc/systemd/system/$SERVICE_NAME.service ]; then
    sudo cp service $P/
    sudo ln -sf $P/service /etc/systemd/system/$SERVICE_NAME.service 
else 
    diff -q $P/service service > /dev/null || (sudo cp service $P/ && sudo systemctl daemon-reload)
fi

sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
