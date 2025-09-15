import threading
import queue
import time
import db_utils
import file_utils
import random

from yandex_api import YandexMusicAPI

api_utils = YandexMusicAPI()

class SyncUtils:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.task_items = set()
        self.lock = threading.Lock()

        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()

        self.progress_operation = ''
        self.progress_entity_type = ''
        self.progress_entity_id = 0

        self.progress_spinner = '*'
        self.i = 0
        self.sequence = ['|', '/', '-', '\\']

        self._spinner_running = threading.Event()
        self._stop_spinner = threading.Event()
        self.progress_cb = None
        self.progress_cb_done = None

    # Queue Manager
    #------------------------#
    # type  # operation # id #
    #------------------------#
    # track # fetch     # ?  #
    # track # download  # ?  #
    # track # favorites #    #

    def obj_task(self, entity_type, operation = 'fetch', entity_id = 0):
        return {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'operation': operation,
        }

    def add_task(self, entity_type, operation = 'fetch', entity_id = 0, fast = False):
        task = self.obj_task(entity_type, operation, entity_id)
        taskfrozen = frozenset(task.items())
        if not fast:
            with self.lock:
                if not self.in_queue(task):
                    self.task_queue.put(task)
                    self.task_items.add(taskfrozen)
                    self.sync_display()
        else:
            self.task_queue.put(task)
            self.task_items.add(taskfrozen)

    def in_queue(self, task):
        return frozenset(task.items()) in self.task_items

    def done_task(self, task):
        self.task_items.discard(frozenset(task.items()))

    def worker(self):
        while True:
            task = self.task_queue.get()
            if task is None:  # Можно для остановки воркера ставить None
                break

            self.do_sync_task(task)


    def do_sync_task(self, task):

        self.progress_entity_type = task['entity_type']
        self.progress_entity_id = task['entity_id']
        self.progress_operation = task['operation']

        self.start_spinner()

        if task['entity_type'] == 'track' and task['operation'] == 'favorites':
            self._sync_favorite_tracks_thread()
        if task['entity_type'] == 'track' and task['entity_id'] > 0 and task['operation'] == 'fetch':
            self._sync_track_thread(task['entity_id'])
        if task['entity_type'] == 'track' and task['entity_id'] > 0 and task['operation'] == 'download':
            self._download_track_thread(task['entity_id'])

        self.stop_spinner()
        self.done_task(self.obj_task(task['entity_type'], task['operation'], task['entity_id']))
        self.sync_display()
        
        if(self.task_queue.qsize() > 0):
            time.sleep(0.1)


    def cancel(self):
        
        self.task_queue.queue.clear()
        
        self.task_queue.all_tasks_done.acquire()
        try:
            self.task_queue.all_tasks_done.notify_all()
        finally:
            self.task_queue.all_tasks_done.release()
        self.task_queue.unfinished_tasks = 0

        self.task_items.clear()


    # update track list

    def sync_favorite_tracks(self):
        self.progress_operation = 'fetch'
        self.progress_entity_type = 'favorite'
        self.progress_entity_id = 'tracks'
        self.start_spinner()
        api_thread = threading.Thread(target=self._sync_favorite_tracks_thread, args=())
        api_thread.start()

    def _sync_favorite_tracks_thread(self):
        try:
            api_tracks = api_utils.get_favorite_tracks()
            favorites_to_store = []
            for tr in api_tracks:
                favorites_to_store.append({'entity_type': 'track', 'entity_id': tr.id})
                db_utils.update_favorites(favorites_to_store)
        finally:
            self.stop_spinner()

    # update track info

    def sync_track(self, entity_id):
        self.progress_operation = 'fetch'
        self.progress_entity_type = 'track'
        self.progress_entity_id = entity_id

        # Запускаем спиннер
        self.start_spinner()

        # Запускаем выполнение задачи в отдельном потоке
        api_thread = threading.Thread(target=self._sync_track_thread, args=(entity_id,))
        api_thread.start()

    def _sync_track_thread(self, entity_id):
        try:
            track_list = api_utils.fetch_track_by_entity_id([entity_id])
            db_utils.update_tracks_from_api(track_list)
        finally:
            self.stop_spinner()

    # download track
    # file_utils.track_download(entity_id, 'favorite_tracks')

    def download_track(self, entity_id):
        self.progress_operation = 'download'
        self.progress_entity_type = 'track'
        self.progress_entity_id = entity_id
        self.start_spinner()
        api_thread = threading.Thread(target=self._download_track_thread, args=(entity_id,))
        api_thread.start()

    def _download_track_thread(self, entity_id):
        try:
            file_utils.track_download(entity_id, 'favorite_tracks')
        finally:
            self.stop_spinner()
    

    def start_spinner(self):
        self._spinner_running.set()
        self._stop_spinner.clear()
        if not hasattr(self, '_spinner_thread') or not self._spinner_thread.is_alive():
            self._spinner_thread = threading.Thread(target=self._spinner_loop, daemon=True)
            self._spinner_thread.start()

    def stop_spinner(self):
        self._spinner_running.clear()
        self._stop_spinner.set()
        if hasattr(self, '_spinner_thread'):
            self._spinner_thread.join()

        self.progress_operation = ''
        self.progress_entity_type = ''
        self.progress_entity_id = 0

        if self.progress_cb_done:
            self.progress_cb_done()

    def _spinner_loop(self):
        while self._spinner_running.is_set():
            self.progress_spinner = f"[{self.sequence[self.i % len(self.sequence)]}]"
            self.i += 1
            self.sync_display()
            time.sleep(0.1)
        self.progress_spinner = '*'
        self.sync_display()

    def sync_display(self):
        if self.progress_cb:
            self.progress_cb()
