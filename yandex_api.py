import os
from dotenv import load_dotenv
from yandex_music import Client
import npyscreen

load_dotenv()
YANDEX_MUSIC_TOKEN = os.getenv('YANDEX_MUSIC_TOKEN')

if not YANDEX_MUSIC_TOKEN:
    raise RuntimeError("YANDEX_MUSIC_TOKEN не найден в .env")

class YandexMusicAPI:
    def __init__(self):
        # Создаем клиента с токеном
        self.client = Client(YANDEX_MUSIC_TOKEN)
        self.client.init()

    def get_favorite_tracks(self):
        # Получаем список избранных треков
        tracks_list = self.client.users_likes_tracks()
        # Возвращаем список объектов TrackShort
        return tracks_list

    def get_favorite_artists(self):
        # Получаем список избранных артистов
        artists_list = self.client.users_likes_artists()
        return artists_list

    def get_favorite_albums(self):
        # Получаем список избранных альбомов
        albums_list = self.client.users_likes_albums()
        return albums_list

    def get_favorite_playlists(self):
        # Получаем список избранных плейлистов
        playlists_list = self.client.users_likes_playlists()
        return playlists_list

    def fetch_track_by_entity_id(self, entity_id):
        """
        Получение объекта трека или списка треков по entity_id или списку entity_id

        entity_id -- int, str или список id (int/str)

        Возвращает один объект трека или список объектов треков.
        """
        try:
            # Преобразуем в список, если передано одно значение
            if not isinstance(entity_id, (list, tuple)):
                entity_ids = [str(entity_id)]
            else:
                entity_ids = [str(eid) for eid in entity_id]

            # Запрос треков
            tracks = self.client.tracks(entity_ids)
            # npyscreen.notify_confirm(f"{tracks}", title=f"Информация по треку {entity_id}")

            # Для каждого объекта трека вызываем fetch_track, чтобы получить полный объект
            # full_tracks = [t.fetch_track() for t in tracks]
            full_tracks = tracks #[]
            """
                py/object: "yandex_music.track.track.Track",
                id, 
                title, 
                artists: [], 
                albums: [], 
                type: "music", 
                cover_uri (%% => m1000x1000), 
                duration_ms,
                file_size: 0,
            """
            """
                py/object: "yandex_music.artist.artist.Artist"
                id, 
                name, 
                cover: "yandex_music.cover.Cover",
            """
            """
                "py/object": "yandex_music.album.album.Album"
                "id": 
                "error": 
                "title": 
                "track_count": 1,
            """

            # Если был один id - возвращаем один объект, иначе список
            # if len(full_tracks) == 1:
            #     return full_tracks[0]
            return full_tracks
        except Exception as e:
            print(f"Ошибка загрузки треков по entity_id {entity_id}: {e}")
            return None