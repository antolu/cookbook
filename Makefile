SHELL := /bin/bash

.PHONY: devinit
devinit:
	source ./tests/tools.sh && devinit
	docker-compose up -d
	DOCKER=TRUE source ./tests/tools.sh && setupEnv

.PHONY: clean
clean: 
	docker-compose down

# TODO: update UWSGI socket
# TODO: move files to appropriate directores
