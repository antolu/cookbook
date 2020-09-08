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
ENV PYTHONPATH $repodir:$PYTHONPATH
$END
EOF
	fi

	if [[ ! -z $DOCKERCOMPOSE ]]; then
		cat <<EOF | sed -i "/\# BEGIN SUBMODULES/r /dev/stdin" $DOCKERCOMPOSE
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
	END="# > END COOKBOOK"

	if [[ ! -z $DOCKERFILE ]]; then
		sed -i "/$BEGIN/,/$END/d" $DOCKERFILE
	fi


	if [[ ! -z $DOCKERCOMPOSE ]]; then
		sed -i "/$BEGIN/,/$END/d" $DOCKERCOMPOSE
	fi
}

installTeXLive() {
    CWD=$PWD
    curl -L http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz -o /tmp/install-tl.tar.gz
    cd /tmp
    tar -xvf install-tl.tar.gz
    cd install-tl-*
    ./install-tl -profile "$CWD"/config/texlive.profile

    cd "$CWD"
    echo 'pathmunge /usr/local/texlive/2020/bin/x86_64-linux' > /etc/profile.d/customshell.sh

    /usr/local/texlive/2020/bin/x86_64-linux/tlmgr install \
        babel-swedish \
        enumitem \
        environ \
        etoolbox \
        fontspec \
        ifsym \
        lastpage \
        latexindent \
        latexmk \
        newunicodechar \
        pgf \
        tcolorbox \
        titlesec \
        trimspaces \
        units \
        wrapfig \
        xcolor \
        xetex
}

installTeXTools() {
    /usr/local/texlive/2020/bin/x86_64-linux/tlmgr install \
    latexindent

    yum install perl perl-open
    cpan install Log::Log4perl Log::Dispatch::File YAML::Tiny
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
