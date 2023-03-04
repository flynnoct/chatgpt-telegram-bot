#!/bin/bash

ps -ef | grep telegram_message_parser.py | grep -v grep | awk '{pid=$2}' | xargs kill -15

./start_bot.sh

