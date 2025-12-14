FROM alpine:latest

RUN apk add --no-cache bash bc jq

WORKDIR /app

COPY data-pipeline.sh .

RUN chmod +x data-pipeline.sh

ENTRYPOINT ["/app/data-pipeline.sh"]

