FROM alpine:latest

RUN apk add --no-cache bash bc

WORKDIR /app

COPY backup-db.sh .

RUN chmod +x backup-db.sh

ENTRYPOINT ["/app/backup-db.sh"]

