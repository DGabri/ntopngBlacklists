FROM python:3.10-slim

WORKDIR /app

# Keep the COPY commands as they are
COPY api_server/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server /app/api_server
COPY config /app/config
COPY utils /app/utils

# Run uvicorn with module path api_server.main:app
ENV PYTHONPATH=/app
CMD ["uvicorn", "api_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
