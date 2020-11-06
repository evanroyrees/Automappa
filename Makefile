.PHONY: clean test env help

help:
	@echo "Please read the 'Makefile' file for available commands"

test:
	python index.py -i test/bins.tsv

env:
	@echo "Creating env name: magmap"
	conda create -n magmap python=3.7 -y
	@echo "(Note: You will need to activate your environment before proceeding with make install"

install: ./requirements.txt
	@echo "Installing dependencies"
	pip3 install --user -r $<