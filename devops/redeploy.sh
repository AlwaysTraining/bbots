#!/bin/bash

# Path to your own script
# http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
pushd . > /dev/null
push_SCRIPT_PATH="${BASH_SOURCE[0]}";
  while([ -h "${push_SCRIPT_PATH}" ]) do
    cd "`dirname "${push_SCRIPT_PATH}"`"
    push_SCRIPT_PATH="$(readlink "`basename "${push_SCRIPT_PATH}"`")";
  done
cd "`dirname "${push_SCRIPT_PATH}"`" > /dev/null
push_SCRIPT_PATH="`pwd`";
popd  > /dev/null

cd $push_SCRIPT_PATH

rm -rf bbot
git clone git@github.com:AlwaysTraining/bbot.git

rm -rf bbots
git clone git@github.com:AlwaysTraining/bbots.git

rm -rf python-google-spreadsheet
git clone git@github.com:AlwaysTraining/python-google-spreadsheet.git
