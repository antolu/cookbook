#!/bin/bash

# TODO: install texlive

CWD=$PWD
SCRIPT_DIR="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

if [[ -z $INSTALLDIR ]]; then
    INSTALLDIR=$PWD
fi

DOCKER=TRUE # need to replace this line with dynamic detection

init() {
    git submodule sync --recursive
    git submodule update --init --recursive --progress
}

devinit() {
    init

    source /dev/stdin <<< "$(curl -L https://gitlab.haochen.lu/server/dockerfile/-/raw/master/tools.sh)"
    installDependencies

    docker-compose up -d

    setupEnv
}

installPackages() {
    echo "Installing Supervisor"
    dnf install -y epel-release
    dnf install -y supervisor

    systemctl enable --now supervisord

    echo "Installing PostgreSQL"
    if [[ -z $DOCKER ]]; then
        dnf install -y postgresql-server
    fi
    dnf install -y postgresql libpq-devel
}

setupPython() {
    if [[ -d "./venv" ]]; then
        echo "venv already installed. Skipping. "
        return 0
    fi

    echo "Creating virtualenv"

    python3 -m virtualenv ./venv
    . ./venv/bin/activate
    pip install -r requirements.txt

    chown -R devuser ./venv
}

configureSupervisor() {
    cp -f ./config/supervisor.cookbook.ini /etc/supervisord.d/cookbook.ini

    supervisorctl reread
    supervisorctl update
}

configurePostgres() {
    alias postgres="docker exec -itu postgres postgres -c"
    docker exec -itu postgres postgres bash -c 'psql -c "CREATE USER cookbook
    WITH PASSWORD "password";"'
    docker exec -itu postgres postgres bash -c "psql -c 'ALTER USER cookbook
    CREATEDB;'"
    docker exec -itu postgres postgres bash -c "psql -c 'CREATE DATABASE
    cookbook;'"
    docker exec -itu postgres postgres bash -c "psql -c 'GRANT ALL PRIVILEGES
    ON DATABASE cookbook TO cookbook;'"
}

setupNginx() {
    if [[ ! -d "/etc/nginx/sites-enabled" ]]; then
        echo "Need to create directories for nginx blocks"
        mkdir -p /etc/nginx/sites-available
        mkdir -p /etc/nginx/sites-enabled

        # need to restore SELinux permissions for created folder in the future
    fi

    echo "Inserting nginx blocks"
    sed -i '/\s{4}server {/,/\s{4}}/ s/^/#/' /etc/nginx/nginx.conf

    # Need to make sure not to insert line twice (upon reinstall or similar)
    sed -i '/include \/etc\/nginx\/conf.d\/\*.conf;/a \\n    include \/etc\/nginx\/sites-enabled\/\*.conf;' /etc/nginx/nginx.conf

    cp -f ./config/nginx.cookbook.conf /etc/nginx/sites-available/cookbook.conf
    ln -s /etc/nginx/sites-available/cookbook.conf /etc/nginx/sites-enabled/cookbook.conf

    systemctl restart nginx

    usermod -aG devuser nginx
}

setupEnv() {
    if [[ -z $DOCKER ]]; then
        echo "Leaving setup to Docker-Compose. Doing nothing. "
    else
        echo "In production environment. Setting up normally."
        setup
    fi
}

createUserGroups() {
    groupadd --system webapps
    useradd  --system --gid webapps --home $INSTALLDIR cookbook

    if [[ -z $DOCKER ]]; then
        chown -R cookbook:users $INSTALLDIR
    else
        usermod -aG webapps devuser
    fi
}

setup() {
    echo "INSTALLDIR is $INSTALLDIR"

    installPackages

    setupPython
    setupNginx

    configureSupervisor
    createUserGroups
}
