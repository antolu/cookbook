#!/bin/bash

python3 -m virtualenv ./venv
. /venv/bin/activate
pip3 install -r requirements.txt

# TODO: deploy to nginx module
# TODO: update UWSGI socket
# TODO: move files to appropriate directores