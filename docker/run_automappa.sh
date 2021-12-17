#!/usr/bin/env bash

set -o errexit

if [ $# -eq 0 ]
  then
    echo "====================================="
    echo " (required) run_automappa arguments"
    echo "--binning         :   default => None"
    echo " (optional) run_automappa arguments"
    echo "--containerport   :   default => 8886"
    echo "--localport       :   default => 8050"
    echo "====================================="
    echo 
    docker run --detach=false --rm evanrees/automappa:latest
    exit 0
fi

if [[ "$*" == *-h* ]];then
    docker run --detach=false --rm evanrees/automappa:latest -h
    exit 0
fi

localport=${localport:-8050}
containerport=${containerport:-8886}
binning=${binning:-none}
# https://brianchildress.co/named-parameters-in-bash/
while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
        #// Optional to see the parameter:value result
        # echo $1 $2 
   fi

  shift
done

# See https://stackoverflow.com/a/4774063/13118765 for desc. of reliable way to get full dirpath
binning_dirname="$( cd -- "$(dirname "$binning")" >/dev/null 2>&1 ; pwd -P )"
binning_filename=$(basename $binning)

echo ":=================== Attention Automappa User ====================:"
echo "Parameters set"
echo "         binning : ${binning}"
echo " binning_dirname : ${binning_dirname}"
echo "binning_filename : ${binning_filename}"
echo "       localport : ${localport}"
echo "   containerport : ${containerport}"
echo 
echo
echo "  *IGNORE* :       http://localhost:${containerport} *IGNORE*     "
echo
echo "  Navigate to ---> http://localhost:${localport}                  "
echo ":----------------------------------------------------------------:"

docker run \
  --publish $localport:$containerport \
  -v $binning_dirname:/binning:rw \
  --detach=false \
  --rm \
  evanrees/automappa:latest --input /binning/$binning_filename --port $containerport --host 0.0.0.0
