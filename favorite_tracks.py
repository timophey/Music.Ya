from yandex_api import YandexMusicAPI
import db_utils

api = YandexMusicAPI()

def get_from_db():
    # Возвращает список строк для npyscreen
    data = db_utils.get_favorite_tracks()
    if not data:
        return []
    return [format_string_for_display(item) for item in data]

def sync_from_api():
    api_tracks = api.get_favorite_tracks()
    favorites_to_store = []
    tracks_to_store = []

    for tr in api_tracks:
        track_id = tr.id
        title = getattr(tr, 'title', '')
        artists_str = ", ".join([ar.name for ar in tr.artists]) if hasattr(tr, 'artists') else "Неизвестный исполнитель"

        # Добавляем в избранное с типом 'track'
        favorites_to_store.append({'entity_type': 'track', 'entity_id': track_id})

        # Добавляем в подробные данные трека
        tracks_to_store.append({
            'yandex_track_id': str(tr.id),
            'title': tr.title,
            'artist': ", ".join([ar.name for ar in tr.artists]) if hasattr(tr, 'artists') else "Неизвестный исполнитель"
        })

    # Обновляем обе таблицы
    db_utils.update_favorites(favorites_to_store)
    db_utils.update_tracks(tracks_to_store)