FROM python:3.10-alpine
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100
WORKDIR /app
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app/main.py .
CMD ["python", "main.py"]
