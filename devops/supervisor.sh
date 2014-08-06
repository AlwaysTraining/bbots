#!/bin/bash

# Path to your own script
# http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
pushd . > /dev/null
start_SCRIPT_PATH="${BASH_SOURCE[0]}";
  while([ -h "${start_SCRIPT_PATH}" ]) do
    cd "`dirname "${start_SCRIPT_PATH}"`"
    start_SCRIPT_PATH="$(readlink "`basename "${start_SCRIPT_PATH}"`")";
  done
cd "`dirname "${start_SCRIPT_PATH}"`" > /dev/null
start_SCRIPT_PATH="`pwd`";
popd  > /dev/null

cd $start_SCRIPT_PATH
. devenv.rc

ps auxw | grep bin/bbotsd.py | grep -v grep > /dev/null

if [ $? != 0 ]
then
echo "Hello,

At $(date) it was determined that the bot server was not running. For your 
continued happiness, the bot server supervisor is pulling down the latest code
and restarting the server.  Would you care to view the latest source changes,
the last 50 lines of the server logs?


bbot Source Changes:
--------------------
$(cd bbot && $(which git) log --pretty=format:'%cr:  %s' --abbrev-commit --date=short --branches -n 10)

bbots Source Changes:
---------------------
$(cd bbots && $(which git) log --pretty=format:'%cr:  %s' --abbrev-commit --date=short --branches -n 10)

Webserver log:
--------------
$(tail -n50 webapp.log)


bbots daemon log:
-----------------
$(tail -n50 bbotsd.log)


pulling latest changes:
-----------------------
$(./pull.sh)


restarting server:
------------------
$(./start.sh)
$(sleep 5)
$(ps auxw | grep bbotsd.py | grep -v grep)

If this was not an unforseen event, and there is a systematic error, you will
receive this email once per hour.  Thank you for your continued dedication to
automation.



Rigorously,
    The Supervisor Cron Job

" | ./botmail.sh "[bbot] Server Restarted by Supervisor"


fi

