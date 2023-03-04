#!/bin/bash

ps -ef | grep telegram_message_parser.py | grep -v grep | awk '{print $2}' | xargs kill -15