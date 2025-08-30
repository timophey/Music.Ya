from yandex_api import YandexMusicAPI
import db_utils

api = YandexMusicAPI()

def get_from_db():
    """
    Получить список избранных артистов из базы для отображения.
    Возвращает список строк, например: "Имя артиста"
    """
    artists = db_utils.get_favorite_artists()
    if not artists:
        return []
    return [a['name'] for a in artists]

def sync_from_api():
    """
    Синхронизировать избранных артистов из API с базой данных.
    Получает данные через YandexMusicAPI и обновляет базу.
    """
    try:
        api_artists = api.get_favorite_artists()
        # api_artists — список объектов yandex_music.Artist или схожей структуры
        db_utils.update_artists(api_artists)
    except Exception as e:
        print(f"Ошибка синхронизации артистов: {e}")
