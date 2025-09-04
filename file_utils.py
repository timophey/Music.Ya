import os

import requests
import db_utils
import datetime
import npyscreen
from log import logging


from yandex_api import YandexMusicAPI

api = YandexMusicAPI()

# tag editor

from mutagen.id3 import (
    ID3, APIC, TIT2, TPE1, TALB, TDRC, TRCK, TPOS, WOAR, COMM, ID3NoHeaderError
)


def extract_year(date_str):
    try:
        if date_str:
            return datetime.datetime.strptime(date_str[:4], "%Y").year
    except Exception:
        pass
    return "EP"

def track_download_path(entity_id):
    tr = db_utils.get_track(entity_id)
    # if not tr.entity_id:
    #     return { "dir_path": dir_path, "filename": filename, "fullpath": os.path.join(dir_path, filename)}
    year = tr['year'] if tr['year'] is not None else extract_year(tr['release_date']) if tr['release_date']  is not None else "EP"
    
    track_number = "00"
    if tr['track_index']:
        track_number = str(tr['track_index']).zfill(2)

    artist_folder = tr['artists_name']
    album_folder = f"{year} - {tr['album_title']}"
    dir_path = os.path.join("storage/downloads", artist_folder, album_folder)
    filename = f"{track_number} - {tr['title']}.mp3"
    # npyscreen.notify_confirm(f"{tr}", title=f"tr")
    # base_path = f"downloads/{tr['artists_name']}/{year} - {tr['album_title']}/{tr['track_index']} - {tr['title']}.mp3"
    return { "dir_path": dir_path, "filename": filename, "fullpath": os.path.join(dir_path, filename)}

def relative_symlink(src, dst):  
    dir = os.path.dirname(dst)  
    src = os.path.relpath(src, dir)  
    return os.symlink(src, dst)

def track_download(entity_id, symlink_to = None):
    # get info from API
    track_list = api.fetch_track_by_entity_id([entity_id])
    for track_obj in track_list:
        # update db
        db_utils.update_tracks_from_api([track_obj])
        # make path
        filepath = track_download_path(track_obj.id)
        # download flie
        os.makedirs(filepath['dir_path'], exist_ok=True)
        track_obj.download(filepath['fullpath'])
        fill_tags(filepath['fullpath'], track_obj)
        # symlink
        if symlink_to:
            symlink_dir  = os.path.join('storage', symlink_to)
            symlink_path = os.path.join(symlink_dir, f"{track_obj.id} - {track_obj.title}.mp3")
            if not os.path.exists(symlink_dir):
                logging.warning(f"mkdir for symlink: {symlink_dir}")
                os.makedirs(symlink_dir, exist_ok=True)
            if not os.path.exists(symlink_path):
                relative_symlink(filepath['fullpath'], f"{symlink_path}")

def fill_tags(filepath, track_obj):
    try:
        audio = ID3(filepath)
    except ID3NoHeaderError:
        audio = ID3()
    
    album = track_obj.albums[0] if track_obj.albums else None
    artists = [artist.name for artist in track_obj.artists] if track_obj.artists else []
    year = "EP"
    if album and album.release_date:
        try:
            year = album.release_date[:4]
        except Exception:
            pass

    track_number = "0"
    total_tracks = "0"
    disc_number = "0"
    if album and album.track_position:
        pos = album.track_position
        if hasattr(pos, 'index'):
            track_number = str(pos.index)
        if hasattr(album, 'track_count'):
            total_tracks = str(album.track_count)
        if hasattr(pos, 'volume'):
            disc_number = str(pos.volume)

    audio.add(TIT2(encoding=3, text=track_obj.title))  # Title
    audio.add(TPE1(encoding=3, text=artists))           # Artist(s)
    audio.add(TALB(encoding=3, text=album.title if album else "Unknown Album"))  # Album
    audio.add(TDRC(encoding=3, text=year))               # Year
    audio.add(TRCK(encoding=3, text=f"{track_number}/{total_tracks}"))  # Track number
    audio.add(TPOS(encoding=3, text=disc_number))        # Disc number

    url = f"https://music.yandex.ru/track/{track_obj.id}"
    audio.add(WOAR(encoding=3, url=url))  # URL tag
    audio.add(COMM(encoding=3, lang='eng', desc='Comment', text=url))  # Comment tag

    cover_uri = None
    if track_obj.cover_uri:
        cover_uri = track_obj.cover_uri
    if album and album.cover_uri:
        cover_uri = album.cover_uri
    if cover_uri:   
        cover_url = cover_uri.replace("%%", "m1000x1000")
        if not cover_url.startswith("http"):
            cover_url = "https://" + cover_url
        try:
            resp = requests.get(cover_url)
            if resp.status_code == 200:
                audio.delall('APIC')
                audio.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=resp.content
                    )
                )
        except Exception as e:
            logging.warning(f"Ошибка при загрузке обложки: {e}")

    audio.save(filepath)


    # track_obj = track.fetch_track()