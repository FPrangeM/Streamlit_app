FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY cadastros.csv .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]