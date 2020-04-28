SHELL := /bin/bash

.PHONY: devinit
devinit:
	DOCKER=TRUE source ./tests/tools.sh && devinit

.PHONY: clean
clean: 
	docker-compose down

reset: clean devinit

# TODO: update UWSGI socket
# TODO: move files to appropriate directores
