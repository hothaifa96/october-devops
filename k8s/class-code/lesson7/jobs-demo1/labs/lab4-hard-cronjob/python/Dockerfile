FROM python:3.11-slim

WORKDIR /app

COPY data-pipeline.py .

RUN chmod +x data-pipeline.py

ENTRYPOINT ["python3", "data-pipeline.py"]

