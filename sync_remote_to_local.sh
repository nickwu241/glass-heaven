#!/bin/sh

PROJECT_NAME='easy-companies-overview'
rsync --exclude='frontend' --exclude='functions' --filter=':- .gitignore' \
    -ave ssh /Users/nickwu/src/github.com/nickwu241/${PROJECT_NAME} "$(terraform output ip)":~/

rsync -ave ssh /Users/nickwu/src/github.com/nickwu241/${PROJECT_NAME}/backend/dist "$(terraform output ip)":~/${PROJECT_NAME}/backend
rsync -ave ssh /Users/nickwu/src/github.com/nickwu241/${PROJECT_NAME}/backend/easy-companies-overview-firebase-adminsdk-7idn2-520e664df3.json "$(terraform output ip)":~/${PROJECT_NAME}/backend