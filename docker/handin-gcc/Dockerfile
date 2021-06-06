FROM ubuntu:18.04

EXPOSE 8580

RUN useradd -ms /bin/bash handin \
    && chown root:handin /home/handin \
    && chmod 1775 /home/handin

RUN apt-get -y update && apt-get -y install \
                    software-properties-common \
                   && add-apt-repository ppa:deadsnakes/ppa \
                   && apt-get -y install \
                        g++ \
                        freeglut3-dev \
                        libglu1-mesa-dev \
                        mesa-common-dev \
                        libomp-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /home/handin
CMD [ "/bin/bash" ]
