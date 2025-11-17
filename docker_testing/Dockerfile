FROM ubuntu:latest

RUN \
    apt update && \
    apt install -y pcmanfm featherpad lxtask xterm

ENV DISPLAY=host.docker.internal:0.0

CMD pcmanfm