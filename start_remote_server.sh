#!/bin/sh

ssh $(terraform output ip) 'cd ~/easy-companies-overview/backend && \
    pipenv install && \
    pipenv run ./start_server.sh'