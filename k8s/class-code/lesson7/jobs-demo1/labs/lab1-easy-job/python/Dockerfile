FROM python:3.11-slim

WORKDIR /app

COPY process-numbers.py .

RUN chmod +x process-numbers.py

ENTRYPOINT ["python3", "process-numbers.py"]

