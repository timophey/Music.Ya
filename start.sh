#!/bin/bash

# Проверка наличия команды python3 -m venv
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "Команда 'python3 -m venv' не найдена или модуль venv не установлен."
    echo "Для установки на Ubuntu/Debian выполните:"
    echo "  sudo apt update && sudo apt install python3-venv"
    echo "Для других ОС установите соответствующий пакет для поддержки venv."
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d ".venv" ]; then
    echo "Виртуальное окружение не найдено, создаем .venv..."
    python3 -m venv .venv
fi

# Активируем виртуальное окружение
source .venv/bin/activate

# Устанавливаем зависимости
if [ -f "requirements.txt" ]; then
    echo "Устанавливаем зависимости из requirements.txt..."
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден."
fi

# Если параметров нет, показываем справку, иначе передаем параметры дальше
if [ $# -eq 0 ]; then
    python3 yandex_music_sync.py --help
else
    python3 yandex_music_sync.py "$@"
fi

# Деактивируем виртуальное окружение (опционально)
deactivate
