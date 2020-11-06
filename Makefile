.PHONY: clean test env help


help:
	@echo "Please read the 'Makefile' file for available commands"

test:
	python index.py -i test/bins.tsv

env:
	@echo "Creating env name: automappa"
	conda create -n automappa python=3.7 -y
	@echo "(Note: You will need to activate your environment before proceeding with make install"

install: ./requirements.txt
	@echo "Installing dependencies"
	pip3 install --user -r $<


clean:
	@rm -rf __pycache__
	@rm -rf apps/__pycache__