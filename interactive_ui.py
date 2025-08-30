import npyscreen
import favorite_tracks
import favorite_artists
import favorite_albums
import favorite_playlists
from favorite_base import FavoritesBaseForm

class MainMenu(npyscreen.ActionForm):
    def create(self):
        self.name = "Главное меню"
        # Добавляем список с вариантами выбора
        self.menu = self.add(npyscreen.TitleSelectOne,
                             max_height=6,
                             name="Выберите раздел",
                             values=[
                                 "Избранные треки",
                                 "Избранные артисты",
                                 "Избранные альбомы",
                                 "Избранные плейлисты",
                                 "Выход"
                             ],
                             scroll_exit=True)
    
    def on_ok(self):
        # Запоминаем выбранный пункт
        choice = self.menu.get_selected_objects()
        if not choice:
            npyscreen.notify_confirm("Пожалуйста, выберите пункт меню", title="Ошибка")
            return
        choice_text = choice[0]
        if choice_text == "Избранные треки":
            self.next_form = 'TRACKS'
        elif choice_text == "Избранные артисты":
            self.next_form = 'ARTISTS'
        elif choice_text == "Избранные альбомы":
            self.next_form = 'ALBUMS'
        elif choice_text == "Избранные плейлисты":
            self.next_form = 'PLAYLISTS'
        else:
            self.next_form = None
        self.parentApp.setNextForm(self.next_form)
        self.editing = False  # Завершаем редактирование, перейдем к afterEditing
    
    def on_cancel(self):
        # При ESC выходим из приложения
        self.next_form = None
        self.parentApp.setNextForm(None)
        self.editing = False

    def afterEditing(self):
        # Переходим на форму, которую изначально выбрали
        self.parentApp.setNextForm(self.next_form)


class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.DISABLE_RESIZE_SYSTEM = True
        self.addForm('MAIN', MainMenu)
        self.addForm('TRACKS', FavoritesBaseForm, name="Избранные треки", favorite_module=favorite_tracks)
        self.addForm('ARTISTS', FavoritesBaseForm, name="Избранные артисты", favorite_module=favorite_artists)
        self.addForm('ALBUMS', FavoritesBaseForm, name="Избранные альбомы", favorite_module=favorite_albums)
        self.addForm('PLAYLISTS', FavoritesBaseForm, name="Избранные плейлисты", favorite_module=favorite_playlists)

if __name__ == '__main__':
    app = MyApp()
    app.run()
