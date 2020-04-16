#!/bin/bash

CWD=$PWD
SCRIPT_DIR="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

init() {
    git submodule sync --recursive
    git submodule update --init --recursive --progress
}

devinit() {
    init

    source ./tests/dockerfile/tools.sh
    installDependencies

    DOCKER=TRUE
}

setupPython() {
    if [[ -d "./venv" ]]; then
        echo "venv already installed. Skipping. "
        return 0
    fi

    python3 -m virtualenv ./venv
    . ./venv/bin/activate
    pip install -r requirements.txt
}

setupEnv() {
    if [[ -z $DOCKER ]]; then
        docker exec -it -u devuser -w /home/cookbook server bash -c "source tests/tools.sh && setupPython"
    else
        setupPython
    fi
}

# TODO: install texlive