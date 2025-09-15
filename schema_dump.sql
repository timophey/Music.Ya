DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS albums;
DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yandex_track_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    artist_ids TEXT,
    artist_id INTEGER,
    artist TEXT,
    album_ids TEXT,
    album_id INTEGER,
    duration INTEGER,
    track_index INTEGER,
    track_count INTEGER,
    disc_number INTEGER,
    local_path TEXT,
    cover_url TEXT,
    url TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yandex_album_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    artist_id INTEGER,
    release_date TEXT,
    year INTEGER,
    cover_uri TEXT,
    url TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yandex_artist_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    bio TEXT,
    url TEXT,
    cover_url TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yandex_playlist_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    owner TEXT,
    url TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE favorites (
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_type, entity_id)
);
