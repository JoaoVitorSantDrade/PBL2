FROM ubuntu:22.04

RUN apt-get update && \
      apt-get -y install sudo

RUN apt-get -y install software-properties-common

RUN add-apt-repository --yes ppa:mosquitto-dev/mosquitto-ppa

RUN add-apt-repository --yes ppa:deadsnakes/ppa

RUN apt update

RUN apt -y install mosquitto

RUN apt -y install mosquitto-clients

RUN apt -y install python3.10

RUN apt -y install python3-pip

RUN python3.10 -m pip install --upgrade pip

RUN pip install flask

RUN pip install paho-mqtt

RUN service mosquitto start

EXPOSE 1883
EXPOSE 1884

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

USER docker

CMD /bin/bash