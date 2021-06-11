FROM ubuntu:18.04

RUN useradd -ms /bin/bash handin \
    && chown root:handin /home/handin \
    && chmod 1775 /home/handin

RUN apt-get -y update && apt-get -y install \
                    software-properties-common \
                   && add-apt-repository ppa:deadsnakes/ppa \
                   && apt-get -y install \
                        strace \
                        lua5.3 && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/lua5.3 /usr/bin/lua

WORKDIR /home/handin
CMD [ "/bin/bash" ]
