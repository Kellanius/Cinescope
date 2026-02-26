# 1. Базовый образ с Python 3.12 (официальный и легкий)
FROM python:3.12-slim-bookworm

# 2. Устанавливаем системные зависимости, нужные для Playwright и сборки пакетов
#    --no-install-recommends чтобы не тащить лишнее
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 3. Устанавливаем Node.js (нужен для testit-adapter-playwright)
#    Используем официальный скрипт для установки NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*


# 4. Устанавливаем зависимости Python (все из requirements.txt)
#    Копируем файл сначала для лучшего кэширования слоев Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Устанавливаем testit-adapter-playwright глобально через npm
RUN npm install -g testit-adapter-playwright

# 6. Устанавливаем браузеры Playwright (без зависимостей ОС, т.к. мы их уже поставили)
RUN playwright install --with-deps chromium

# 7. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /workspace

# 8. Команда по умолчанию (будет переопределяться Jenkins'ом)
CMD ["pytest", "--version"]