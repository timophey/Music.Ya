import logging
import os

# Настройка логгера
os.makedirs('storage/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,  # уровень логов, начиная с DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("storage/logs/debug.log", encoding='utf-8'),  # Запись в файл
        # logging.StreamHandler()  # Вывод в консоль
    ]
)
