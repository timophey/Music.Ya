import sqlite3

def create_tables_from_dump(db_path='music_sync.db', dump_path='schema_dump.sql'):
    with open(dump_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sql_script)  # выполнение всего дампа сразу
    conn.commit()
    conn.close()
    print(f"База данных создана и инициализирована из {dump_path} в {db_path}")
