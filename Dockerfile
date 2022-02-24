FROM ubuntu:20.04
MAINTAINER BeetleChunks

ENV DEBIAN_FRONTEND "noninteractive"

RUN apt update -y \
	&& apt upgrade -y \
	&& apt install dos2unix -y \
	&& apt install wget -y \
	&& apt install tmux -y \
	&& apt install nano -y \
	&& apt install python3 -y \
	&& apt install python3-pip -y

RUN wget https://chilkatdownload.com/9.5.0.89/chilkat2-9.5.0-python-3.8-x86_64-linux.tar.gz \
	&& tar -xzf ./chilkat2-9.5.0-python-3.8-x86_64-linux.tar.gz \
	&& cd ./chilkat2-9.5.0-python-3.8-x86_64-linux \
	&& python3 ./installChilkat.py -g \
	&& python3 ./testChilkat.py \
	&& cd .. \
	&& rm ./chilkat2-9.5.0-python-3.8-x86_64-linux.tar.gz

ADD ./ /wb3

RUN chmod -R 755 /wb3 \
	&& chmod +x /wb3/WeBeater3.py

RUN pip3 install -r /wb3/requirements.txt

WORKDIR "/wb3"

CMD ["/bin/bash"]