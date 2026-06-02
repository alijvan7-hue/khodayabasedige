FROM python:3.12-slim

# متغیرهای محیطی
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# دایرکتوری کار
WORKDIR /app

# نصب وابستگی‌های Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد پروژه
COPY . .

# اجرای migration و start ربات
CMD ["sh", "-c", "alembic upgrade head && python main.py"]