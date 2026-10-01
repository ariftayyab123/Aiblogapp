FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Production server. runserver is a development server and must not serve
# traffic; override the command locally if you want autoreload.
CMD ["sh", "-c", "gunicorn ai_blog.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --timeout 120"]
