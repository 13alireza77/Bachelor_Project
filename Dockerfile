FROM python:3.9
MAINTAINER Alireza Alidoosti
ENV TZ=Asia/Tehran
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV RUN_MODE=web
ENV SECRET_KEY='django-insecure-v!j39i%(9j_8(s@pbpf!h-k-gelyx!=*68e#&fj+u5$7!_*f0f'
ENV DEBUG=True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y
RUN pip3 install --upgrade pip
ADD ./requirements.txt ./requirements.txt
RUN pip3 install -r  requirements.txt
COPY ./ /.