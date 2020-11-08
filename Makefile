# python version
PYTHON = python3

.PHONY = help setup test run clean

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make setup"
	@echo "To test the project type make test"
	@echo "To run the project type make run"
	@echo "------------------------------------"

test:
	${PYTHON} -m pytest
	
run:
	python ./pipeline/etl.py

clean:
	rm -r *.project