FROM python:3.9-slim

# working directory
WORKDIR /app

# requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]