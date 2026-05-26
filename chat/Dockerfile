FROM python:3.11-slim

WORKDIR /app

COPY chat/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chat/ .

EXPOSE 8001

CMD ["python", "main.py"]
