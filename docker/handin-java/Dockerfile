FROM openjdk:11.0.1-slim

EXPOSE 8580

RUN useradd -ms /bin/bash handin \
    && chown root:handin /home/handin \
    && chmod 1775 /home/handin

WORKDIR /home/handin
CMD [ "/bin/bash" ]
