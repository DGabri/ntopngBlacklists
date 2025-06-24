FROM python:3.10-slim

WORKDIR /app

# install requirements
COPY producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy entire src folder content to /app
COPY . .

ENV PYTHONPATH=/app

CMD ["python", "producer/producer.py"]