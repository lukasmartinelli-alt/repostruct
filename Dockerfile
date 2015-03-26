FROM python:3-onbuild
RUN wget https://github.com/lukasmartinelli/redis-pipe/releases/download/v1.3/redis-pipe && chmod +x redis-pipe
