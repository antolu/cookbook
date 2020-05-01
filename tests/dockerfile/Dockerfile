FROM gitlab.haochen.lu:5050/server/dockerfile

LABEL maintainer="anton96lu@gmail.com"

ARG ROOT_DIR=/home/cookbook
WORKDIR $ROOT_DIR
COPY . .

ENV INSTALLDIR=$ROOT_DIR

RUN bash -c "source tests/tools.sh && \
    installPackages && \
    setupNginx && \
    configureSupervisor || true && \
    createUserGroups && \
    installTeXLive"

ENV PATH /usr/local/texlive/2020/bin/x86_64-linux:$PATH

RUN rm -rf ..?* .[!.]* *