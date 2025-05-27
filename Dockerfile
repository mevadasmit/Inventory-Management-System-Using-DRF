FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=hospital_inventory_management.settings

WORKDIR /app

# Install netcat-openbsd (provides nc)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["gunicorn", "hospital_inventory_management.wsgi:application", "--bind", "0.0.0.0:8000"]
