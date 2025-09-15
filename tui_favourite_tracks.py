import npyscreen
import threading
import time
import os
from tui_common_form import TuiCommonForm
from tui_common_table_form import TuiCommonTableForm
from widget_spinner import WidgetSpinner
import tui_table_utils
import db_utils
import file_utils
from sync_utils import SyncUtils



class TuiFavouriteTracksForm( TuiCommonTableForm ):

    help_strings = [
        "i - Fetch and update Track data"
    ]

    def create( self ):
        # Menu
        self.menu = self.new_menu( name = "Select Action")
        self.menu.addItem("Sync Favourites Track  Short", self.sync_favorite_track_shorts, "s")
        self.menu.addItem("Sync Favourites Tracks All", self.sync_favorite_tracks_info_all)
        self.menu.addItem("Sync Favourites Tracks Missed", self.sync_favorite_tracks_info_missed)
        self.menu.addItem("Sync Downloads  Tracks Missed", self.sync_favorite_tracks_file_missed)
        # 
        self.menu.addItem("<- Go back", self.go_to_back, "b")
        # 
        self.menu.addItem("Exit", self.exit_form, "x")
        # Widgets
        self.spinner_widget = WidgetSpinner( form = self )
        # Make table widgets and others from SUPER
        super().create()
        # bind actions
        self.bind()

    # Methods of TuiFavouriteTracksForm

    def bind( self ):
        self.sync = SyncUtils()
        self.sync.progress_cb = self.sync_progress
        self.sync.progress_cb_done = self.refresh_display
        self.list_widget.add_handlers({
            'i': self.bind_key_i,
            'd': self.bind_key_d,
            27: self.bind_key_27,
            })
        
    def sync_progress( self ):
        self.spinner_widget.widget.value = self.sync.progress_spinner
        self.spinner_widget.widget.display()
        self.refresh_display()

    def bind_key_i( self, _input ):
        if self.list_item:
            self.sync.add_task('track','fetch',self.list_item['entity_id'])
            self.list_widget.cursor_line += 1
            # item = self.list_item
            # npyscreen.notify(f"in {self.sync.in_queue( self.sync.obj_task('track', 'fetch', item['entity_id']) )}")
            # if self.sync.progress_entity_id:
            #     self.sync.sync_done()
            # else:
            #     self.sync.sync_track(self.list_item['entity_id'])

    def bind_key_d( self, _input ):
        if self.list_item:
            self.sync.add_task('track','download',self.list_item['entity_id'])
            self.list_widget.cursor_line += 1
            # if self.sync.progress_entity_id:
            #     self.sync.sync_done()
            # else:
            #     self.sync.download_track(self.list_item['entity_id'])
            
    # Escape
    def bind_key_27( self, _input ):
        self.sync.cancel()

    def sync_favorite_track_shorts( self ):
        self.sync.sync_favorite_tracks()

    def sync_favorite_tracks_info( self ):
        pass

    def sync_favorite_tracks_info_missed( self ):
        list = db_utils.get_favorite_tracks()
        for item in list:
            if not item['track_id']:
                self.sync.add_task('track','fetch',item['entity_id'], fast = True)

    def sync_favorite_tracks_info_all( self ):
        list = db_utils.get_favorite_tracks()
        for item in list:
            self.sync.add_task('track','fetch',item['entity_id'], fast = True)

    def sync_favorite_tracks_file_missed( self ):
        list = db_utils.get_favorite_tracks()
        for item in list:
            if not os.path.exists(file_utils.track_download_path(item['entity_id'])['fullpath']):
                self.sync.add_task('track','download',item['entity_id'], fast = True)

    # def download_track( self )
        
    
    # Overwrite TuiCommonTableForm methods

    def get_list( self ):
        # Возвращает список строк для npyscreen
        is_in_progress = self.sync.progress_entity_type == 'track' and self.sync.progress_entity_id > 0
        data = db_utils.get_favorite_tracks() if (not is_in_progress) else self.list_data
        if not data:
            return []
        table_data = []
        for item in data:            
            status = None # None, QFetch, QFile, File
            if item['entity_id'] == self.sync.progress_entity_id:
                if self.sync.progress_operation == 'fetch':
                    status = f"{self.sync.progress_spinner} ob"
                if self.sync.progress_operation == 'download':
                    status = f"{self.sync.progress_spinner} dl"
            elif self.sync.in_queue( self.sync.obj_task('track', 'fetch', item['entity_id']) ):
                status = 'QFetch'
            elif self.sync.in_queue( self.sync.obj_task('track', 'download', item['entity_id']) ):
                status = 'QFile'
            elif item['track_id'] and os.path.exists(file_utils.track_download_path(item['entity_id'])['fullpath']):
                status = 'File'
#            status = os.path.exists(file_utils.track_download_path(item['entity_id'])['fullpath']) if item['track_id'] else False

            item.update({'status': status})
        
        self.list_data = data
        return data

    def get_columns( self ):
        return ['entity_id', 'title', 'artists_name', 'album_title', 'year','status', 'path']

    def get_column_widths( self ):
        return [15, 32, 32, 32, 4, 6, 50]

