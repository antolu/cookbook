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

setupNginx() {
    if [[ ! -d "/etc/nginx/sites-enabled" ]]; then
        echo "Need to create directories for nginx blocks"
        mkdir -p /etc/nginx/sites-available
        mkdir -p /etc/nginx/sites-enabled

        # need to restore SELinux permissions for created folder in the future
    fi
    sed -i '/\s{4}server {/,/\s{4}}/ s/^/#/' /etc/nginx/nginx.conf

    # Need to make sure not to insert line twice (upon reinstall or similar)
    sed -i '/include \/etc\/nginx\/conf.d\/\*.conf;/a \\n    include \/etc\/nginx\/sites-enabled\/\*.conf;' /etc/nginx/nginx.conf

    cp -f ./tests/nginx/cookbook.conf /etc/nginx/sites-available/cookbook.conf
    ln -s /etc/nginx/sites-available/cookbook.conf /etc/nginx/sites-enabled/cookbook.conf

    systemctl restart nginx

    usermod -aG devuser nginx
}

setupEnv() {
    SETUPUSER="
    setupPython
    "
    SETUPADMIN="
    setupNginx
    "
    if [[ -z $DOCKER ]]; then
        docker exec -itw /home/cookbook server bash -c "source tests/tools.sh && $SETUPADMIN"
        docker exec -it -u devuser -w /home/cookbook server bash -c "source tests/tools.sh && $SETUPUSER"
    else
        setupPython
    fi
}

# TODO: install texlive