# Sử dụng Python 3.10
FROM python:3.10-slim

# Cài đặt FFmpeg và các thư viện Âm thanh cốt lõi (Opus + Sodium)
RUN apt-get update && \
    apt-get install -y ffmpeg libopus-dev libsodium-dev libffi-dev git && \
    rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục
WORKDIR /app

# Copy code
COPY . /app

# Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Chạy bot
CMD ["python", "main.py"]
