import sqlite3
import npyscreen

class FavoritesBaseForm(npyscreen.ActionForm):
    def create(self):
        self.list_widget = self.add(npyscreen.MultiLine, values=[], max_height=-4, scroll_exit=True)
        self.status = self.add(npyscreen.FixedText, value="Статус: готов")
        self.hotkeys = self.add(npyscreen.FixedText, value="Горячие клавиши: Ctrl+S — Синхронизация | Esc — Назад")
        self.add_handlers({"^S": self.sync_data})

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        try:
            conn = sqlite3.connect('music.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tracks.title, tracks.artist
                FROM favorites
                JOIN tracks ON favorites.entity_id = tracks.id
                WHERE favorites.entity_type = 'track';
            """)
            rows = cursor.fetchall()
            conn.close()

            if rows:
                display_list = [f"{title} — {artist}" for title, artist in rows]
            else:
                display_list = ["Избранных треков нет"]

            self.list_widget.values = display_list
            self.status.value = f"Загружено {len(rows)} треков"
        except Exception as e:
            self.list_widget.values = [f"Ошибка загрузки: {str(e)}"]
            self.status.value = "Ошибка"
        self.display()

    def sync_data(self, *args, **kwargs):
        self.status.value = "Синхронизация..."
        self.display()
        self.favorite_module.sync_from_api()
        self.update_list()
        self.status.value = "Синхронизировано"
        self.display()

    def on_ok(self):
        self.parentApp.setNextForm('MAIN')
        self.editing = False

    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')
        self.editing = False
