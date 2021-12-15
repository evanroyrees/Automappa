#!/usr/bin/env bash

if [ ! -f $1 ] || [ ! -f $2 ]
then
	echo "Please provide valid filepaths"
	echo -e "e.g.:\ncommand autometa.binning.main.tsv autometa.markers.tsv"
	exit 1
fi

python index.py --binning-main $1 --markers $2 --debug
