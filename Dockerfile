# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12.10-alpine3.20	 AS base

WORKDIR /svc

COPY requirements.txt requirements.txt
RUN rm -rf /var/cache/apk/* && rm -rf /tmp/*
RUN apk update && apk add --update python3 && rm -rf /var/cache/apk/*
RUN pip wheel -r requirements.txt --wheel-dir=/svc/wheels


FROM docker.io/library/python:3.12.10-alpine3.20	

COPY --from=base /svc /svc
WORKDIR /svc

RUN pip install --no-index --find-links=/svc/wheels -r requirements.txt
WORKDIR /app
COPY app.py .
COPY client.py .
COPY static static

EXPOSE 80

CMD ["waitress-serve", "--port", "80", "app:app"]
