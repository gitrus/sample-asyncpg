FROM python:3.5

# install build dependencies
RUN apt-get -qq update \
  && pip3 install --upgrade pip \
  && mkdir /app && cd app

ARG sample=.

ADD requirements.txt /app/

RUN pip3 --no-cache-dir install -r /app/requirements.txt

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

ENV APP_PATH "/app"

WORKDIR /app
VOLUME /app

ENTRYPOINT ["/bin/bash", "everlast.sh"]