# Парсер YT на Python

Собирает информацию о каналах (Кол-во Подписчиков, просмотры, Дата создания, Страна, Ссылки на соц сеть) и записывает всё в папку "./results" и в базу данных sqlite3.

## Как использовать?
1. Настроить файл config.py
```python
USE_PROXY = False                  # Использовать Прокси: True - Да False - Нет
PROTOCOL_PROXY = 'http'            # Протокол прокси: http или socks5
DATABASE_NAME = './database.db'    # Имя Базы Данных
BLACKLIST_COUNTRY = [              # 
    'Russia',                      # 
    'Taiwan'                       # 
]                                  # Список стран, которое нужно исключить. Название страны брать из ютуб в английском интерфейсе
YEAR = 2020                        # До какого года брать каналы
SUBSCRIBERS = 1000                 # От какого числа подписчиков
VIEWS = 1000                       # От сколько просмотров
```
2. Настроить файлы keywoards.txt и proxy.txt

>Файл proxy.txt пример:
```
username:password@ip:port
username:password@ip:port
username:password@ip:port

// Протокол прокси зависит от того какой вы поставили в файле config.py
// Поддерживаются http и socks5
```
#
> Файл keywords.txt. Обычный запрос для поиска видео, после которого собираются вся информация о каналах
```
Запрос
```

3. Установить все зависимости
```cmd
python -m venv venv
vens/Scripts/activate
pip install -r requirements.txt
```

>Далее можно запускать парсер
```cmd
python main.py
```


