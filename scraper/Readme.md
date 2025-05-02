# Telegram Scraper

## Описание (RU)
Telegram Scraper - это инструмент для отслеживания сообщений из определенных чатов Telegram с использованием API Telegram. Скрипт отслеживает указанные в конфигурации чаты и выводит текстовое содержимое сообщений в консоль.

### Требования
- Python 3.7+
- Pyrogram
- python-dotenv
- uvloop

### Установка
1. Клонируйте репозиторий
2. Установите зависимости:
   ```
   pip install pyrogram python-dotenv uvloop
   ```
3. Создайте файл `.env` в корневой директории проекта со следующими переменными:
   ```
   API_ID=ваш_api_id
   API_HASH=ваш_api_hash
   ```

### Настройка
В файле `config.py` вы можете настроить список чатов для отслеживания:
```python
chats_to_follow = ["ID_чата_1", "ID_чата_2", "me"]
```

### Запуск
```
python server.py
```

## Description (EN)
Telegram Scraper is a tool for monitoring messages from specific Telegram chats using the Telegram API. The script monitors chats specified in the configuration and outputs the text content of messages to the console.

### Requirements
- Python 3.7+
- Pyrogram
- python-dotenv
- uvloop

### Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install pyrogram python-dotenv uvloop
   ```
3. Create a `.env` file in the project root directory with the following variables:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```

### Configuration
In the `config.py` file, you can configure the list of chats to monitor:
```python
chats_to_follow = ["chat_ID_1", "chat_ID_2", "me"]
```

### Running
```
python server.py
```

## Получение API_ID и API_HASH (RU) / Getting API_ID and API_HASH (EN)

### RU
1. Перейдите на [my.telegram.org](https://my.telegram.org/)
2. Войдите в свой аккаунт
3. Перейдите в раздел "API development tools"
4. Создайте новое приложение
5. Скопируйте полученные API_ID и API_HASH в файл .env

### EN
1. Go to [my.telegram.org](https://my.telegram.org/)
2. Log in to your account
3. Navigate to "API development tools"
4. Create a new application
5. Copy the API_ID and API_HASH to your .env file
