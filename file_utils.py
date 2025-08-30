import os
import db_utils
import datetime
import npyscreen

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
    dir_path = os.path.join("downloads", artist_folder, album_folder)
    filename = f"{track_number} - {tr['title']}.mp3"
    # npyscreen.notify_confirm(f"{tr}", title=f"tr")
    # base_path = f"downloads/{tr['artists_name']}/{year} - {tr['album_title']}/{tr['track_index']} - {tr['title']}.mp3"
    return { "dir_path": dir_path, "filename": filename, "fullpath": os.path.join(dir_path, filename)}
