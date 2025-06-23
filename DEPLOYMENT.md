# Руководство по развертыванию

## Развертывание на Replit

Приложение оптимизировано для запуска на Replit:

1. **Импорт проекта** в Replit
2. **Настройка секретов** в панели Secrets:
   - `SESSION_SECRET`: секретный ключ для сессий
   - `OPENROUTER_API_KEY`: ваш API ключ OpenRouter
3. **Запуск** - Replit автоматически установит зависимости и запустит приложение

## Локальное развертывание

### Подготовка системы

#### Ubuntu/Debian
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и системных зависимостей
sudo apt install python3 python3-pip python3-venv
sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
sudo apt install fonts-dejavu fonts-dejavu-core fonts-dejavu-extra

# Для работы с изображениями
sudo apt install libjpeg-dev zlib1g-dev
```

#### CentOS/RHEL
```bash
# Установка EPEL репозитория
sudo yum install epel-release

# Установка зависимостей
sudo yum install python3 python3-pip python3-devel
sudo yum install tesseract tesseract-langpack-rus tesseract-langpack-eng
sudo yum install dejavu-sans-fonts dejavu-serif-fonts

# Для работы с изображениями
sudo yum install libjpeg-turbo-devel zlib-devel
```

#### macOS
```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка зависимостей
brew install python3 tesseract
```

### Установка приложения

1. **Клонирование и настройка**
```bash
git clone <repository-url>
cd material-analysis-app

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate для Windows

# Установка зависимостей
pip install -r requirements.txt
```

2. **Настройка переменных окружения**
```bash
# Создание файла .env
cat > .env << EOF
SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
OPENROUTER_API_KEY=your-openrouter-api-key-here
EOF
```

3. **Компиляция переводов**
```bash
python3 compile_translations.py
```

4. **Тестовый запуск**
```bash
python3 main.py
```

## Продакшн развертывание

### С использованием Gunicorn + Nginx

1. **Установка веб-сервера**
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. **Конфигурация Nginx**
```bash
sudo nano /etc/nginx/sites-available/material-analysis
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Редирект на HTTPS (рекомендуется)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL сертификаты (настройте Let's Encrypt)
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Максимальный размер загружаемых файлов
    client_max_body_size 16M;
    
    # Проксирование к приложению
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Таймауты
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Статические файлы
    location /static/ {
        root /path/to/your/app;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Логи
    access_log /var/log/nginx/material-analysis.access.log;
    error_log /var/log/nginx/material-analysis.error.log;
}
```

3. **Активация конфигурации**
```bash
sudo ln -s /etc/nginx/sites-available/material-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. **Systemd сервис для приложения**
```bash
sudo nano /etc/systemd/system/material-analysis.service
```

```ini
[Unit]
Description=Material Analysis Flask Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=/path/to/your/app/.env
ExecStart=/path/to/your/app/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    main:app

Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
```

5. **Создание директорий для логов**
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

6. **Запуск сервиса**
```bash
sudo systemctl daemon-reload
sudo systemctl enable material-analysis
sudo systemctl start material-analysis
sudo systemctl status material-analysis
```

### SSL сертификат с Let's Encrypt

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Docker развертывание

1. **Создание Dockerfile**
```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Компиляция переводов
RUN python compile_translations.py

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
```

2. **Docker Compose**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SESSION_SECRET=${SESSION_SECRET}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./temp_analysis:/app/temp_analysis
    restart: unless-stopped
```

3. **Запуск с Docker**
```bash
# Создание .env файла
echo "SESSION_SECRET=$(openssl rand -hex 32)" > .env
echo "OPENROUTER_API_KEY=your-api-key" >> .env

# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## Мониторинг и обслуживание

### Логирование
- Приложение: `/var/log/gunicorn/`
- Nginx: `/var/log/nginx/`
- Systemd: `journalctl -u material-analysis -f`

### Резервное копирование
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/material-analysis"
APP_DIR="/path/to/your/app"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Архивирование приложения
tar -czf $BACKUP_DIR/app_$DATE.tar.gz $APP_DIR

# Очистка старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Мониторинг производительности
```bash
# Установка htop для мониторинга системы
sudo apt install htop

# Мониторинг процессов Gunicorn
ps aux | grep gunicorn

# Проверка использования памяти
free -h

# Проверка дискового пространства
df -h
```

## Решение проблем

### Проблемы с памятью
- Уменьшите количество воркеров Gunicorn
- Добавьте swap файл
- Оптимизируйте обработку изображений

### Проблемы с производительностью
- Настройте кэширование статических файлов
- Используйте CDN для статических ресурсов
- Оптимизируйте размеры изображений

### Проблемы с OCR
- Проверьте установку Tesseract
- Убедитесь в наличии языковых пакетов
- Проверьте права доступа к файлам