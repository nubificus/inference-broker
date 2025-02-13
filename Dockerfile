# syntax=docker/dockerfile:1
FROM python:3.12.3-alpine AS base

WORKDIR /svc

COPY requirements.txt requirements.txt
RUN rm -rf /var/cache/apk/* && rm -rf /tmp/*
RUN apk update && apk add --update python3 && rm -rf /var/cache/apk/* && \
    pip wheel -r requirements.txt --wheel-dir=/svc/wheels


FROM python:3.12.3-alpine

COPY --from=base /svc /svc
WORKDIR /svc

RUN pip install --no-index --find-links=/svc/wheels -r requirements.txt
WORKDIR /app
COPY app.py .
COPY client.py .

EXPOSE 80

# CMD ["gunicorn", "--workers", "1", "-b", "0.0.0.0:80", "app:app"]
CMD ["python", "app.py"]