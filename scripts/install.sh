#!/bin/bash


if [ ! -d "$PYENV" ]; then
	echo "Creating virtual environment..."
	virtualenv -p /usr/bin/python3 $PYENV --system-site-packages

	echo "Activating virtual environment..."
	. ./$PYENV/bin/activate

	echo "Installing requirements into '$PYENV'..."
	pip install -r requirements.txt
fi

