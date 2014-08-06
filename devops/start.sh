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
flock -n bbotsd.lock nohup bbotsd.py &> webapp.log &
