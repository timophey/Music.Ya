import sqlite3

DB_PATH = "music_sync.db"

def update_favorites(favorites_list):
    """
    favorites_list - список словарей с ключами: entity_type, entity_id
    Например: [{'entity_type': 'track', 'entity_id': 12345}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for fav in favorites_list:
        cursor.execute("""
            INSERT OR IGNORE INTO favorites (entity_type, entity_id)
            VALUES (?, ?);
        """, (fav['entity_type'], fav['entity_id']))
    conn.commit()
    conn.close()

def get_favorite_tracks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artists.name AS artist, tracks.title
        FROM favorites
        JOIN tracks ON favorites.entity_id = tracks.id
        LEFT JOIN artists ON tracks.artist_id = artists.id
        WHERE favorites.entity_type = 'track'
        ORDER BY tracks.title
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'artist': r[0] if r[0] else 'Неизвестный', 'title': r[1]} for r in rows]

def update_tracks(tracks_list):
    """
    tracks_info - список словарей с ключами: id, title, artist
    Например: [{'id': 12345, 'title': 'Song Name', 'artist': 'Artist Name'}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for t in tracks_list:
        # Убедитесь, что 'yandex_track_id' есть в словаре и не None
        cursor.execute("""
            INSERT OR REPLACE INTO tracks (yandex_track_id, title, artist)
            VALUES (?, ?, ?)
        """, (t['yandex_track_id'], t['title'], t['artist']))
    conn.commit()
    conn.close()

def get_favorite_artists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artists.name
        FROM favorites
        JOIN artists ON favorites.entity_id = artists.id
        WHERE favorites.entity_type = 'artist'
        ORDER BY artists.name
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'name': r[0]} for r in rows]

def update_artists(api_artists):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for artist in api_artists:
        cursor.execute("""
            INSERT OR REPLACE INTO artists (yandex_artist_id, name, bio, url)
            VALUES (?, ?, ?, ?)
        """, (
            artist.id,
            artist.name,
            getattr(artist, 'description', None),
            getattr(artist, 'link', None)
        ))

        cursor.execute("SELECT id FROM artists WHERE yandex_artist_id=?", (artist.id,))
        artist_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT OR IGNORE INTO favorites (entity_type, entity_id)
            VALUES ('artist', ?)
        """, (artist_id,))
    conn.commit()
    conn.close()

def get_favorite_albums():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artists.name AS artist, albums.title
        FROM favorites
        JOIN albums ON favorites.entity_id = albums.id
        LEFT JOIN artists ON albums.artist_id = artists.id
        WHERE favorites.entity_type = 'album'
        ORDER BY albums.title
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'artist': r[0] if r[0] else 'Неизвестный', 'title': r[1]} for r in rows]

def update_albums(api_albums):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for album in api_albums:
        # Вставляем или обновляем артиста
        cursor.execute("""
            INSERT OR IGNORE INTO artists (yandex_artist_id, name)
            VALUES (?, ?)
        """, (album.artist.id, album.artist.name))
        cursor.execute("SELECT id FROM artists WHERE yandex_artist_id=?", (album.artist.id,))
        artist_id = cursor.fetchone()[0]

        # Вставляем или обновляем альбом
        cursor.execute("""
            INSERT OR REPLACE INTO albums
            (yandex_album_id, title, artist_id, release_date, cover_url, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            album.id,
            album.title,
            artist_id,
            getattr(album, 'release_date', None),
            getattr(album.cover, 'uri', None) if getattr(album, 'cover', None) else None,
            getattr(album, 'link', None)
        ))

        cursor.execute("SELECT id FROM albums WHERE yandex_album_id=?", (album.id,))
        album_id = cursor.fetchone()[0]

        # Вставляем запись в избранное
        cursor.execute("""
            INSERT OR IGNORE INTO favorites (entity_type, entity_id)
            VALUES ('album', ?)
        """, (album_id,))
    conn.commit()
    conn.close()

def get_favorite_playlists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title
        FROM favorites
        JOIN playlists ON favorites.entity_id = playlists.id
        WHERE favorites.entity_type = 'playlist'
        ORDER BY title
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'title': r[0]} for r in rows]

def update_playlists(api_playlists):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for playlist in api_playlists:
        cursor.execute("""
            INSERT OR REPLACE INTO playlists (yandex_playlist_id, title, owner, url)
            VALUES (?, ?, ?, ?)
        """, (
            playlist.id,
            playlist.title,
            getattr(playlist, 'owner', None),
            getattr(playlist, 'link', None)
        ))
        cursor.execute("SELECT id FROM playlists WHERE yandex_playlist_id=?", (playlist.id,))
        playlist_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT OR IGNORE INTO favorites (entity_type, entity_id)
            VALUES ('playlist', ?)
        """, (playlist_id,))
    conn.commit()
    conn.close()
