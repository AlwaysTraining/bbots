#!/bin/bash
msg=$1


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
cd bbot
git add .
git commit -m "Pushed from deployment server: $msg"
git push

cd ../bbots

git add .
git commit -m "Pushed From Deployment server: $msg"
git push

