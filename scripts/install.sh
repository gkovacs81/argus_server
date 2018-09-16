#!/bin/bash


if [ ! -d "$PYENV" ]; then
	# temporary unset the PYTHONPATH variable to avoid pip installation problems
	TEMP=$PYTHONPATH
	unset PYTHONPATH
	echo "Creating virtual environment..."
	virtualenv -p /usr/bin/python3 $PYENV --system-site-packages

	echo "Activating virtual environment..."
	. ./$PYENV/bin/activate

	echo "Installing requirements into '$PYENV'..."
	pip install -r requirements.txt
	
	export PYTHONPATH=$TEMP
fi

