FROM python:3-onbuild
RUN wget https://github.com/lukasmartinelli/redis-pipe/releases/download/v1.2/redis-pipe && chmod +x redis-pipe
