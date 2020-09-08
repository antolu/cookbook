# Cookbook

A Django application for storing and visualizing my recipes. Currently works by uploading recipe files formatted with [QML](https://gitlab.haochen.lu/queubit/python-qml).

## Deploy for testing and development

For development and testing purposes it is recommended to use [webapp-base](https://gitlab.haochen.lu/server/webapp-base) to serve the application, which comes with a Docker-compose setup.
Setup is then simply cloning webapp-base, running `make init/devinit` and supplying the repository name `server/cookbook`.

## Deploy for production

TBD.
