FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# We use gunicorn to handle the web traffic properly on Render
CMD gunicorn main:app --bind 0.0.0.0:8080 --worker-class gthread --threads 4 & python main.py
