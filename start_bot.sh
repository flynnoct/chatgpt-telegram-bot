#!/bin/bash
# This script start a Python program named telegram_message_parser.py and run it in the background

nohup python3 telegram_message_parser.py >/dev/null 2>&1 &
echo "Bot has been started successfully"
