FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Run both consumer and API using a simple shell script
CMD ["sh", "-c", "python consumer.py & uvicorn api:app --host 0.0.0.0 --port 8001"]
