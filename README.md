# Сервис подбора материала для конструкции

Веб-приложение на Flask для выбора материала по запросу и техническим документам с использованием искусственного интеллекта. Поддерживает распознавание текста (OCR), многоязычный интерфейс и генерацию PDF отчетов.

## Возможности

- 🔍 **OCR распознавание** - извлечение текста из изображений документов
- 🤖 **ИИ анализ** - анализ материалов с помощью Google Gemini
- 🌐 **Многоязычность** - поддержка русского и английского языков
- 📄 **PDF отчеты** - генерация подробных отчетов с поддержкой кириллицы
- 🎨 **Адаптивный дизайн** - современный интерфейс для всех устройств

## Технологический стек

- **Backend**: Flask, Python 3.11+
- **ИИ**: Google Gemini 2.5 Flash Lite (через OpenRouter API)
- **OCR**: Tesseract OCR
- **PDF**: ReportLab с поддержкой Unicode
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Стили**: Bootstrap 5

## Требования

### Системные зависимости
- Python 3.11 или выше
- Tesseract OCR
- Шрифты DejaVu (для корректного отображения кириллицы в PDF)

### Python пакеты
- Flask
- Flask-Babel
- Pillow
- pytesseract
- reportlab
- requests
- numpy
- faiss-cpu
- python-dotenv

## Установка и запуск

### Локальная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd material-analysis-app
```

2. **Установка системных зависимостей (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
sudo apt install fonts-dejavu fonts-dejavu-core fonts-dejavu-extra
```

3. **Создание виртуального окружения**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

4. **Установка Python зависимостей**
```bash
pip install -r requirements.txt
```

5. **Настройка переменных окружения**
Создайте файл `.env` в корне проекта:
```env
SESSION_SECRET=your-secret-key-here
OPENROUTER_API_KEY=your-openrouter-api-key
```

6. **Компиляция переводов**
```bash
python compile_translations.py
```

7. **Запуск приложения**
```bash
python main.py
```

Приложение будет доступно по адресу: http://localhost:5000

### Развертывание на сервере

#### Использование Gunicorn

1. **Установка Gunicorn**
```bash
pip install gunicorn
```

2. **Запуск с Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
```

#### Nginx конфигурация (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    client_max_body_size 16M;
}
```

#### Systemd сервис

Создайте файл `/etc/systemd/system/material-analysis.service`:

```ini
[Unit]
Description=Material Analysis Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable material-analysis
sudo systemctl start material-analysis
```

## Получение API ключа

1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/)
2. Получите API ключ в личном кабинете
3. Добавьте ключ в переменные окружения

## Структура проекта

```
├── services/               # Бизнес-логика
│   ├── ai_service.py      # Сервис ИИ анализа
│   ├── ocr_service.py     # OCR обработка
│   ├── pdf_service_unicode.py  # Генерация PDF
│   └── vector_service.py  # Векторный поиск
├── templates/             # HTML шаблоны
├── static/               # CSS, JS, изображения
├── translations/         # Файлы переводов
├── utils/               # Утилиты
├── uploads/             # Загруженные файлы
├── temp_analysis/       # Временные файлы анализа
├── app.py              # Основное приложение Flask
├── config.py           # Конфигурация
└── main.py            # Точка входа
```

## Использование

1. **Откройте приложение** в браузере
2. **Выберите язык** интерфейса (русский/английский)
3. **Введите описание** материала или технических требований
4. **Загрузите изображение** (опционально) для OCR распознавания
5. **Нажмите "Анализировать"** для получения результатов
6. **Скачайте PDF отчет** с результатами анализа

## Поддерживаемые форматы изображений

- PNG
- JPEG/JPG
- Максимальный размер: 16 МБ

## Решение проблем

### OCR не работает
```bash
# Проверьте установку Tesseract
tesseract --version

# Установите дополнительные языковые пакеты
sudo apt install tesseract-ocr-rus tesseract-ocr-eng
```

### Проблемы с кириллицей в PDF
```bash
# Установите шрифты DejaVu
sudo apt install fonts-dejavu-core
```

### Ошибки ИИ анализа
- Проверьте правильность API ключа OpenRouter
- Убедитесь в наличии интернет соединения
- Проверьте лимиты API

## Лицензия

MIT License
