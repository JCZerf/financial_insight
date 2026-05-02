FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2 e Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instala os navegadores do Playwright com suas dependências
RUN playwright install --with-deps chromium

# Copia o código da aplicação
COPY . /app

# Expõe a porta 8000
EXPOSE 8000

# Script de entrada para executar migrações e iniciar o servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
