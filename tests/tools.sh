#!/bin/bash

installStylesheet () {
  CWD=$PWD
  cd /tmp

  git clone https://gitlab.haochen.lu/queubit/cookbook-stylesheet.git cookbook-stylesheet
  cd cookbook-stylesheet
  bash install.sh
  cd $CWD
}

runAll() {
  installStylesheet
}
