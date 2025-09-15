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

def get_track(entity_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            tracks.title, tracks.id as track_id, track_index, track_count, disc_number,
            artists.name as artists_name,
            albums.title as album_title, albums.release_date, albums.year
        FROM tracks
        LEFT JOIN artists ON tracks.artist_id = artists.yandex_artist_id
        LEFT JOIN albums ON tracks.album_id = albums.yandex_album_id
        WHERE tracks.yandex_track_id = ?
    """, (int(entity_id),))
    rows = cursor.fetchall()
    if not rows:
        return {}
    keys = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(keys, row)) for row in rows][0]
    
def get_favorite_tracks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #  id, entity_id
    cursor.execute("""
        SELECT 
            favorites.entity_id, favorites.added_at,
            tracks.title, tracks.id as track_id,
            artists.name as artists_name,
            albums.title as album_title, albums.year
        FROM favorites
        LEFT JOIN tracks ON favorites.entity_id = tracks.yandex_track_id
        LEFT JOIN artists ON tracks.artist_id = artists.yandex_artist_id
        LEFT JOIN albums ON tracks.album_id = albums.yandex_album_id
        WHERE favorites.entity_type = 'track'
        ORDER BY favorites.added_at
    """)
    rows = cursor.fetchall()
    keys = [desc[0] for desc in cursor.description]
    conn.close()
    return [dict(zip(keys, row)) for row in rows]
    # return [{'id': r[0], } for r in rows]
    # return rows

def get_favorite_tracks_bac():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artists.name AS artist, tracks.title
        FROM favorites
        LEFT JOIN tracks ON favorites.entity_id = tracks.id
        LEFT JOIN artists ON tracks.artist_id = artists.yandex_artist_id
        LEFT JOIN albums ON tracks.artist_id = albums.yandex_album_id
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

def insert_or_replace(table_name: str, obj: dict):
    keys = obj.keys()
    placeholders = ', '.join(['?'] * len(keys))
    columns = ', '.join(keys)
    sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    values = tuple(obj[k] for k in keys)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def update_tracks_from_api(tracks_list):
    # print(track); 
    for track in tracks_list:

        track_index = 0
        track_count = 0
        disc_number = 0

        for album in track.albums:
            if album and album.track_position:
                pos = album.track_position
                if hasattr(pos, 'index'):
                    track_index = str(pos.index)
                if hasattr(album, 'track_count'):
                    track_count = str(album.track_count)
                if hasattr(pos, 'volume'):
                    disc_number = str(pos.volume)
                break

        track_dict = {
            "yandex_track_id": track.id,
            "title": track.title,
            "artist_id": track.artists[0].id,
            "artist_ids": ','.join(str(artist.id) for artist in track.artists),
            "album_id": track.albums[0].id,
            "album_ids": ','.join(str(album.id) for album in track.albums),
            "cover_url": track.cover_uri,
            "track_index": track_index,
            "track_count": track_count,
            "disc_number": disc_number,
            "duration": track.duration_ms
        }
        insert_or_replace('tracks', track_dict)
        update_artists_from_api(track.artists)
        update_albums_from_api(track.albums)

def update_artists_from_api(items):
    for item in items:
        insert_or_replace('artists', {
            "yandex_artist_id": item.id,
            "name": item.name,
            "url": f"https://music.yandex.ru/artist/{item.id}",
        })

def update_albums_from_api(items):
    for item in items:
        insert_or_replace('albums', {
            "yandex_album_id": item.id,
            "title": item.title,
            "url": f"https://music.yandex.ru/album/{item.id}",
            "release_date": item.release_date,
            "year": item.year,
        })


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
            (yandex_album_id, title, artist_id, release_date, cover_uri, url)
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
