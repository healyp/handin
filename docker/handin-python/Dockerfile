FROM python:3

EXPOSE 8580

RUN useradd -ms /bin/bash handin
RUN chown root:handin /home/handin
RUN chmod 1775 /home/handin

WORKDIR /home/handin
CMD [ "/bin/bash" ]
