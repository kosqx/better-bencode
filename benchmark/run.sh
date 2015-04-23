#! /bin/bash

if [ ! -d "$DIRECTORY" ]; then
    virtualenv --no-site-packages venv
fi

source venv/bin/activate
pip install -r requirements.txt
python benchmark.py
deactivate
