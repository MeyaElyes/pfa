FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY stations/ ./stations/

CMD ["python", "stations/agilAgentStation.py"]
