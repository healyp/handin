FROM openjdk:11.0.1-slim

RUN useradd -ms /bin/bash handin \
    && chown root:handin /home/handin \
    && chmod 1775 /home/handin

RUN apt-get -y update && apt-get -y install \
                    software-properties-common \
                   && add-apt-repository ppa:deadsnakes/ppa \
                   && apt-get -y install \
                        strace

WORKDIR /home/handin
CMD [ "/bin/bash" ]
