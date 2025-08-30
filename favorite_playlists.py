from yandex_api import YandexMusicAPI
import db_utils

api = YandexMusicAPI()

def get_from_db():
    """
    Получить список избранных плейлистов из базы для отображения.
    Возвращает список строк, например: "Имя плейлиста"
    """
    playlists = db_utils.get_favorite_playlists()
    if not playlists:
        return []
    return [p['title'] for p in playlists]

def sync_from_api():
    """
    Синхронизировать избранные плейлисты из API с базой данных.
    Получить данные через YandexMusicAPI и обновить базу.
    """
    try:
        api_playlists = api.get_favorite_playlists()
        # api_playlists — список объектов плейлистов
        db_utils.update_playlists(api_playlists)
    except Exception as e:
        print(f"Ошибка синхронизации плейлистов: {e}")
