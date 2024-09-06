FROM python:3.13.0a1-alpine as builder
COPY . /app
WORKDIR /app
RUN pip install flake8==3.8.4
RUN flake8 --ignore=E501,F401,W605 .
RUN pip wheel . --no-cache-dir --wheel-dir /usr/src/app/wheels

FROM python:3.13.0a1-alpine
ENV PYTHONUNBUFFERED 1
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels/ \
    && apk --no-cache add git openssh-client
WORKDIR /app
ENTRYPOINT ["terrafile"]
