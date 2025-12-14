FROM python:3.11-slim

WORKDIR /app

COPY backup-db.py .

RUN chmod +x backup-db.py

ENTRYPOINT ["python3", "backup-db.py"]

