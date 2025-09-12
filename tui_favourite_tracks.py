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
        self.menu.addItem("Sync Favourites TrackShort", self.sync_favorite_tracks, "s")
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
            # if self.sync.progress_entity_id:
            #     self.sync.sync_done()
            # else:
            #     self.sync.sync_track(self.list_item['entity_id'])

    def bind_key_d( self, _input ):
        if self.list_item:
            self.sync.add_task('track','download',self.list_item['entity_id'])
            # if self.sync.progress_entity_id:
            #     self.sync.sync_done()
            # else:
            #     self.sync.download_track(self.list_item['entity_id'])
            
    # Escape
    def bind_key_27( self, _input ):
        self.sync.cancel()

    def sync_favorite_tracks( self ):
        self.sync.sync_favorite_tracks()
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
            status = os.path.exists(file_utils.track_download_path(item['entity_id'])['fullpath']) if item['track_id'] else False
            if item['entity_id'] == self.sync.progress_entity_id:
                status = self.sync.progress_spinner
            item.update({'status': status})
        
        self.list_data = data
        return data

    def get_columns( self ):
        return ['entity_id', 'title', 'artists_name', 'album_title', 'year','status', 'path']

    def get_column_widths( self ):
        return [15, 32, 32, 32, 4, 6, 50]

