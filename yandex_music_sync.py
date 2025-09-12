import sys
import os

VENV_DIR = '.venv'

def check_venv():
    if not os.path.isdir(VENV_DIR):
        print(f"Виртуальное окружение '{VENV_DIR}' не найдено.")
        print(f"Для создания выполните команду:\npython3 -m venv {VENV_DIR}")
        sys.exit(1)

def print_help():
    help_text = """
Использование:
  python3 yandex_music_sync.py --create-db    Создать структуру SQLite базы из schema_dump.sql
  python3 yandex_music_sync.py --interactive  Запустить интерактивный интерфейс
  python3 yandex_music_sync.py --tui          Запустить терминальный интерфейс
  python3 yandex_music_sync.py --help         Показать эту справку
"""
    print(help_text)

def main():
    check_venv()

    if len(sys.argv) < 2:
        print("Параметры не указаны. Для справки используйте --help")
        return

    arg = sys.argv[1]
    if arg == '--help':
        print_help()
    elif arg == '--create-db':
        import create_db
        create_db.create_tables_from_dump()
    elif arg == '--interactive':
        import interactive_ui
        interactive_ui.MyApp().run()
    elif arg == '--tui':
        import tui
        tui.TuiApp().run()
    else:
        print(f"Неизвестный параметр: {arg}")
        print_help()

if __name__ == "__main__":
    main()
