#!/bin/bash
ps aux | grep 'python /home/ubuntu/play/bbots/bin/bbotsd.py' | grep -v grep | awk '{print $2}' | xargs kill

while ps aux | grep python | grep /home/ubuntu/play/bbots/bin/bbotsd.py | grep -v grep > /dev/null ; do echo "closing..." && sleep 1; done
