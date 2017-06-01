#!/usr/bin/env bash

if ! [ -d kmad_web/frontend/static/libs ] ; then
    curl https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash
    . ~/.nvm/nvm.sh
    nvm install v4.4.0
    npm install -g bower
    bower install --allow-root
fi

docker-compose -f docker-compose.yml -f docker-compose-dev.yml up
