# This tells Render to use a system that HAS Python 3.10 already installed
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy your files into the system
COPY . .

# Install the libraries from your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start your bot
CMD ["python", "main.py"]
