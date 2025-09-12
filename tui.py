import npyscreen
from tui_common_form import TuiCommonForm
from tui_favourite_tracks import TuiFavouriteTracksForm

class TuiMainForm( TuiCommonForm ):
    def create( self ):
        super().create()
        self.menu = self.new_menu( name = "Select Action")
        self.menu.addItem("Favourite Tracks", self.go_to_favourite_tracks, "t")
        self.menu.addItem("Exit", self.exit_form, "x")    

    def go_to_favourite_tracks( self ):
        self.parentApp.switchForm( "FAVOURITE_TRACKS" )

class TuiApp( npyscreen.NPSAppManaged ):
    def onStart( self ):
        self.addForm("MAIN", TuiMainForm, name = "Yandex Music Sync TUI Home")
        self.addForm("FAVOURITE_TRACKS", TuiFavouriteTracksForm, name = "Favourite Tracks")