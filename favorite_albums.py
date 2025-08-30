from yandex_api import YandexMusicAPI
import db_utils

api = YandexMusicAPI()

def get_from_db():
    """
    Получить список избранных альбомов из базы для отображения.
    Возвращает список строк, например: "Исполнитель - Название альбома"
    """
    albums = db_utils.get_favorite_albums()
    if not albums:
        return []
    return [f"{a['artist']} - {a['title']}" for a in albums]

def sync_from_api():
    """
    Синхронизировать избранные альбомы из API с базой данных.
    Получает данные через YandexMusicAPI и обновляет базу.
    """
    try:
        api_albums = api.get_favorite_albums()
        # api_albums - список объектов Album или схожих
        db_utils.update_albums(api_albums)
    except Exception as e:
        print(f"Ошибка синхронизации альбомов: {e}")
