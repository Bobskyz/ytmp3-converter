FROM python:3.11-slim

RUN apt-get update && apt-get install -y nodejs npm ffmpeg \
    && ln -s /usr/bin/nodejs /usr/bin/node \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PORT=5000
EXPOSE ${PORT}

CMD ["python", "app.py"]