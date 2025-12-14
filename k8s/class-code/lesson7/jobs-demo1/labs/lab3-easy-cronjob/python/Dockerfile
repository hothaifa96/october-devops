FROM python:3.11-slim

WORKDIR /app

COPY cleanup-logs.py .

RUN chmod +x cleanup-logs.py

ENTRYPOINT ["python3", "cleanup-logs.py"]

