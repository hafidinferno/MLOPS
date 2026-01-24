FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

# We assume artifacts and data are mounted as volumes
# CMD uvicorn api:app --host 0.0.0.0 --port 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
