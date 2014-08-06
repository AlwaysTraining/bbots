#!/bin/bash
msg=$1


# Path to your own script
# http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
pushd . > /dev/null
status_SCRIPT_PATH="${BASH_SOURCE[0]}";
  while([ -h "${status_SCRIPT_PATH}" ]) do
    cd "`dirname "${status_SCRIPT_PATH}"`"
    status_SCRIPT_PATH="$(readlink "`basename "${status_SCRIPT_PATH}"`")";
  done
cd "`dirname "${status_SCRIPT_PATH}"`" > /dev/null
status_SCRIPT_PATH="`pwd`";
popd  > /dev/null

cd $status_SCRIPT_PATH
cd bbot
git status

cd ../bbots

git status

