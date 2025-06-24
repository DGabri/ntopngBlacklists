FROM python:3.10-slim

WORKDIR /app

# install requirements
COPY consumer/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy files
COPY consumer/consumer.py /app/
COPY config/config_manager.py /app/
COPY config/config.yaml /app/
COPY utils/redis_utils.py /app/

# Run the consumer script
CMD ["python", "consumer.py"]
