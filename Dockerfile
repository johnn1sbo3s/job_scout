FROM python:3.12-slim

# 1. Instala dependências do sistema para o Chromium (Patchright) e o Cron
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    cron \
    && rm -rf /var/lib/apt/lists/*

# 2. Define diretório de trabalho
WORKDIR /app

# 3. Copia os arquivos de definição de pacotes
# O pip moderno instala direto do pyproject.toml
COPY pyproject.toml ./

# 4. Instala as dependências no Python global do container
# Usamos --no-cache-dir para manter a imagem leve
RUN pip install --no-cache-dir .

# 5. Instala os navegadores do Patchright
RUN patchright install chromium

# 6. Copia o código e arquivos de configuração
COPY app/ ./app/
COPY profile.yaml resume.md ./

# 7. Configura o Cron
COPY crontab /etc/cron.d/job-scout-cron
RUN chmod 0644 /etc/cron.d/job-scout-cron && \
    crontab /etc/cron.d/job-scout-cron && \
    touch /var/log/cron.log

# 8. Salva as variáveis de ambiente para o cron e inicia os serviços
# Valor padrão (produção)
ENV APP_ENV=prod

# CMD condicional baseado em APP_ENV
CMD sh -c '\
  printenv | grep -v "no_proxy" >> /etc/environment; \
  if [ "$APP_ENV" = "dev" ]; then \
      echo "Rodando em modo DEV: mantendo container vivo"; \
      tail -f /dev/null; \
  else \
      echo "Rodando em modo PROD: cron + main + tail do log"; \
      cron && \
      python -m app.main && \
      tail -f /var/log/cron.log; \
  fi'