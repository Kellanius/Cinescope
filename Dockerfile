# 1. Базовый образ с Python 3.12
FROM python:3.12-slim-bookworm

# 2. Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    sed \
    && rm -rf /var/lib/apt/lists/*

# 3. Установка Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 4. Копирование Python-зависимостей
COPY requirements.txt .

# Удаляем старые версии testit-пакетов (на случай, если они уже были)
RUN pip uninstall -y testit-adapter-pytest testit-python-commons testit-api-client || true

# Фиксируем совместимые версии Test IT
RUN pip install --no-cache-dir \
    testit-api-client==7.5.2 \
    testit-python-commons==3.12.2 \
    testit-adapter-pytest==3.12.2 \
    testit-cli==2.8.2

# Устанавливаем остальные зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Установка testit-adapter-playwright (через npm)
RUN npm install -g testit-adapter-playwright

# 6. Установка браузеров Playwright
RUN playwright install --with-deps chromium

# 7. Рабочая директория
WORKDIR /workspace

# 8. Команда по умолчанию
CMD ["pytest", "--version"]