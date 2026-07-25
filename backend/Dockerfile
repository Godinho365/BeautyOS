# BeautyOS backend — imagem de aplicação (walking skeleton).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro (cache de camada).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código.
COPY . .

EXPOSE 8000

# Em produção use gunicorn; para o skeleton, o runserver é suficiente em dev.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
