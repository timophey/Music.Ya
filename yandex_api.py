import os
from dotenv import load_dotenv
from yandex_music import Client

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
