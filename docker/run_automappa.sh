#!/bin/bash

set -o errexit
set -o nounset

DEFAULT_IMAGE_TAG="main"
DEFAULT_CONTAINER_PORT=8886
DEFAULT_LOCAL_PORT=8050

if [ $# -eq 0 ]
  then
    echo "      run_automappa.sh Arguments     "
    echo "====================================="
    echo "Required"
    echo "    --binning       : Path to main binning table"
    echo "    --markers       : Path to markers table"
    echo
    echo "Optional"
    echo "    --imagetag      : (default -> ${DEFAULT_IMAGE_TAG})"
    echo "    --containerport : (default -> ${DEFAULT_CONTAINER_PORT})"
    echo "    --localport     : (default -> ${DEFAULT_LOCAL_PORT})"
    echo "    --help          : (see automappa parameters)"
    echo "====================================="
    echo 
    exit 0
fi

if [[ "$*" == *-h* ]];then
    docker run --detach=false --rm evanrees/automappa:$IMAGE_TAG -h
    exit 0
fi

imagetag=${imagetag:-main}
localport=${localport:-$DEFAULT_LOCAL_PORT}
containerport=${containerport:-$DEFAULT_CONTAINER_PORT}
binning=${binning:-none}
markers=${markers:-none}
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
markers_dirname="$( cd -- "$(dirname "$markers")" >/dev/null 2>&1 ; pwd -P )"
markers_filename=$(basename $markers)

echo ":=================== Attention Automappa User ====================:"
echo "docker Automappa settings"
echo "        imagetag : ${imagetag}"
echo "       localport : ${localport}"
echo "   containerport : ${containerport}"
echo " binning_dirname : ${binning_dirname}"
echo "binning_filename : ${binning_filename}"
echo " markers_dirname : ${markers_dirname}"
echo "markers_filename : ${markers_filename}"
echo 
echo "Automappa settings"
echo "         binning : ${binning}"
echo "         markers : ${markers}"
echo 
echo ":----------------------------------------------------------------:"
echo
echo "  *IGNORE* :       http://localhost:${containerport} *IGNORE*     "
echo
echo "  Navigate to ---> http://localhost:${localport}                  "
echo ":----------------------------------------------------------------:"
docker run \
    --publish $localport:$containerport \
    --detach=false \
    -v $binning_dirname:/binning:rw \
    -v $markers_dirname:/markers:ro \
    --rm \
    evanrees/automappa:$imagetag \
      --binning-main /binning/$binning_filename \
      --markers /markers/$markers_filename \
      --port $containerport \
      --host 0.0.0.0


# docker run -v $PWD:/binning:rw -v $PWD:/markers:ro -p 8050:8886 --rm evanrees/automappa:develop --binning-main /binning/SRR13258664.bacteria.hdbscan.main.tsv --markers /markers/SRR13258664.bacteria.markers.tsv --port 8886
