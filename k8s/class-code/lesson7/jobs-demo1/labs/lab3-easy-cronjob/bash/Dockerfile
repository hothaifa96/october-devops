FROM alpine:latest

RUN apk add --no-cache bash findutils

WORKDIR /app

COPY cleanup-logs.sh .

RUN chmod +x cleanup-logs.sh

ENTRYPOINT ["/app/cleanup-logs.sh"]

