FROM alpine:latest

RUN apk add --no-cache bash bc

WORKDIR /app

COPY process-numbers.sh .

RUN chmod +x process-numbers.sh

ENTRYPOINT ["/app/process-numbers.sh"]

