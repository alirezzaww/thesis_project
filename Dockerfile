FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install required system libraries
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    libdbus-1-dev \
    libglib2.0-dev \
    libcairo2-dev \
    libsystemd-dev \
    libgirepository1.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "-m", "src.api"]
