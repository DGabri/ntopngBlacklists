FROM python:3.10-slim

WORKDIR /app

# install requirements
COPY producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy files
COPY producer/producer.py .
COPY config/config.yaml /app/
COPY config/config_manager.py .
COPY utils/alerts_generator.py .


CMD ["python", "producer.py"]
