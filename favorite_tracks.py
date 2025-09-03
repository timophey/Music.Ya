from yandex_api import YandexMusicAPI
import db_utils
import file_utils
import npyscreen
# import use_tracks_api.py
import json
import jsonpickle
from json import JSONEncoder
import threading
import os

api = YandexMusicAPI()

current_list = []
current_list_limit = 10
current_position = 0
current_parent = None

def get_table_columns():
    return ['entity_id', 'title', 'artists_name', 'album_title', 'year','present', 'path']

def get_table_widths():
    return [15, 32, 32, 32, 4, 5, 50]

def bind(self):
    self.list_widget.add_handlers({
        'i': action_fetch_current_track
    })
    self.list_widget.add_handlers({
        'd': action_show_current_download_path
    })
    self.list_widget.add_handlers({
        'D': action_download_current_track,
    })
    self.load_missed = self.add(npyscreen.ButtonPress, name="Load missed")
    self.load_missed.whenPressed = load_missed_tracks_all

def on_scroll():
    load_missed_tracks()
def on_ready():
    # threading.Thread(target=load_missed_tracks, daemon=True).start()
    load_missed_tracks()

def load_missed_tracks():
    # npyscreen.notify_confirm(f"# load_missed_tracks current_list_limit = {current_list_limit}, current_position = {current_position}, len = {len(current_list)}", title=f"Информация")
    global load_and_save_track_info
    # npyscreen.notify_confirm(f"[{current_position}:{current_position+current_list_limit}]") #  => {len(list)}
    if current_position % current_list_limit == 0 or current_position == 0:
        list = current_list[current_position:current_position+current_list_limit]#visible_count
        # npyscreen.notify_confirm(f"{list}", title=f"Информация")
        for item in list:
            # npyscreen.notify_confirm(f"{item}", title=f"Информация")
            if item['track_id'] is None:
                # npyscreen.notify_confirm(f"{item}", title=f"Load")
                load_and_save_track_info(item['entity_id'])
        # будем тут подгружать инфу по трекам, которых нет в базе, и сохранять в базу

def load_missed_tracks_all():
    global current_position 
    global current_list_limit
    global load_missed_tracks
    pages_count = len(current_list) // current_parent.list_widget.height
    # npyscreen.notify_confirm(f"pages_count {pages_count}")
    for i in range(pages_count + 1):
        go_to_line = i * current_parent.list_widget.height
        if go_to_line < len(current_parent.list_widget.values):
            # npyscreen.notify_confirm(f"page #{i}, start from {i * current_parent.list_widget.height}")
            current_parent.list_widget.start_display_at = go_to_line
            current_parent.list_widget.cursor_line = go_to_line
            current_parent.list_widget.display()
            current_position = go_to_line
            current_list_limit = current_parent.list_widget.height
            load_missed_tracks()

def load_and_save_track_info(entity_id):
    # npyscreen.notify_confirm(f"{entity_id}", title=f"Load")
    # Здесь ваш запрос к API, вместо заглушки используйте реальный вызов
    current_parent.start_spinner()
    track_list = api.fetch_track_by_entity_id([entity_id])
    db_utils.update_tracks_from_api(track_list)
    current_parent.stop_spinner()
    if current_parent:
        current_parent.refresh_display()
    # save as dump
    try:    
        os.makedirs('storage/json', exist_ok=True)
        with open(f"storage/json/track_{entity_id}_data.json", 'w') as f:
            f.write(jsonpickle.encode(track_list[0]))
    except:
        pass
    # return        
    return track_list[0]

def load_and_show_track_info(entity_id):
    track = load_and_save_track_info(entity_id)

    # Формируем текст из данных
    # info_text = "\n".join(f"{key}: {value}" for key, value in track_info.items())

    # Показываем модальное окно с информацией
    npyscreen.notify_confirm(jsonpickle.encode(track), title=f"Информация по треку {entity_id}")
    # npyscreen.notify_confirm(f"{current_parent}", title=f"Информация по треку {entity_id}")

def get_current_entity_id():
    idx = current_position
    if idx < 0 or idx >= len(current_list):
        return
    line = current_list[idx]
    entity_id = line.get('entity_id')
    return entity_id

def action_fetch_current_track(_input):
    idx = current_position
    # npyscreen.notify_confirm(f"{current_list}", title=f"Информация по треку {idx}")
    if idx < 0 or idx >= len(current_list):
        return
    line = current_list[idx]
    entity_id = line.get('entity_id')
    load_and_show_track_info(entity_id)

def action_show_current_download_path(_input):
    idx = current_position
    if idx < 0 or idx >= len(current_list):
        return    
    line = current_list[idx]
    # npyscreen.notify_confirm(f"{line}", title=f"Информация по треку {idx}")
    entity_id = line.get('entity_id')
    # npyscreen.notify_confirm(f"{entity_id}", title=f"action_show_current_download_path")
    current_parent.debug_widget.value = file_utils.track_download_path(entity_id)['fullpath']
    current_parent.debug_widget.display()


def get_from_db():
    global current_list
    # Возвращает список строк для npyscreen
    data = db_utils.get_favorite_tracks()
    if not data:
        return []
    table_data = []
    # data = []
    for item in data:
        # table_data.append(item)        
        present = os.path.exists(file_utils.track_download_path(item['entity_id'])['fullpath']) if item['track_id'] else False
        item.update({'present': present})
        #missed
        #exists
    # npyscreen.notify_confirm(f"{data}", title=f"data")
    current_list = data
    # load_missed_tracks()
    # threading.Thread(target=load_missed_tracks, daemon=True).start()
    
    return data
    # return [format_string_for_display(item) for item in data]

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

    # Обновляем обе таблицы
    db_utils.update_favorites(favorites_to_store)
    # db_utils.update_tracks(tracks_to_store)


def action_download_current_track(_input):
    entity_id = get_current_entity_id()
    # npyscreen.notify_confirm(f"download {entity_id}", title=f"data")
    current_parent.start_spinner()
    file_utils.track_download(entity_id, 'favorite_tracks')
    current_parent.stop_spinner()
    current_parent.list_widget.cursor_line += 1
    current_parent.list_widget.display()

    # track_download()