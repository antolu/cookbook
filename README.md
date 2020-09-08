# Cookbook

My recipes and a .yml -> PDF generator script

## Deploy for testing and development

Only compatible with Linux. Currently supported distributions are Ubuntu, Debian and Arch Linux.

The following command installs `docker`, `docker-compose` and launches 2 docker containers: a CentOS 8 container containing the nginx web server with `/home/cookbook` is bound to the repository root.

```bash
make devinit
```

Execute commands inside the docker container (as user `devuser`) using

```bash
docker exec -it -u devuser server [command]
```

or open up an interactive shell inside the server container (as user `devuser`) using

```bash
docker exec -it -u devuser -w /home/cookbook server zsh
```

The default `sudo` password is `pwd`.

## Deploy for production

TBD.
