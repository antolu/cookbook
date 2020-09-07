#!/bin/bash

init () {
	if [[ ! -z $SETTINGSPY ]]; then
		sed -i "/^INSTALLED_APPS = \[/a\ \ \ \ 'cookbook.apps.CookbookConfig'," $SETTINGSPY
	fi

	if [[ ! -z $URLSPY ]]; then
		sed -i "/^urlpatterns = \[/a\ \ \ \ path('cookbook/', include('cookbook.urls'))," $URLSPY
	fi

	BEGIN="# > BEGIN COOKBOOK"
	END="# > END COOKBOOK"

	if [[ ! -z $DOCKERFILE ]]; then
		cat <<EOF | sed -i "/^\# BEGIN SUBMODULES/r /dev/stdin" $DOCKERFILE
$BEGIN
RUN bash -c "source $repodir/tests/tools.sh && installTeXLive"
ENV PATH /usr/local/texlive/2020/bin/x86_64-linux:\$PATH
$END
EOF
	fi

	if [[ ! -z $DOCKERCOMPOSE ]]; then
		cat <<EOF | sed -i "/^\# BEGIN SUBMODULES/r /dev/stdin" $DOCKERCOMPOSE
$BEGIN
        source $repodir/tests/tools.sh
        installStylesheet
        python ./manage.py makemigrations cookbook
$END
EOF
	fi
}

remove () {
	if [[ ! -z $SETTINGSPY ]]; then
		sed -i "/CookbookConfig/d" $SETTINGSPY
	fi

	if [[ ! -z $URLSPY ]]; then
		sed -i "/cookbook.urls/d" $URLSPY
	fi

	BEGIN="# > BEGIN COOKBOOK"
	END="# END > COOKBOOK"

	if [[ ! -z $DOCKERFILE ]]; then
		sed -i "/^$BEGIN/,/^$END/d" $DOCKERFILE
	fi


	if [[ ! -z $DOCKERCOMPOSE ]]; then
		sed -i "/^$BEGIN/,/^$END/d" $DOCKERCOMPOSE
	fi
}

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
