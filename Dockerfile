FROM python:3-onbuild
RUN wget https://github.com/lukasmartinelli/pusred/releases/download/v0.9/pusred && chmod +x pusred
