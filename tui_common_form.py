import npyscreen

class TuiCommonForm( npyscreen.FormWithMenus ):

    def create( self ):
        self.add_handlers({
            ord('q'): self.exit_form,
            ord('Q'): self.exit_form,
        })

    def while_waiting(self):
        pass  # Можно оставить пустым или использовать для фоновых задач

    def handle_quit(self, _input):
        self.parentApp.setNextForm(None)  # Завершить приложение
        self.editing = False  # Остановить редактирование формы

    def _handle_input(self, key):
        if key in (ord('q'), ord('Q')):
            npyscreen.notify_confirm("pressed Q", editw=1)
            self.handle_quit(key)
            return True
        return super()._handle_input(key)

    def go_to_back( self ):
        self.parentApp.switchFormPrevious()

    def exit_form( self, _input = None ):
        self.parentApp.switchForm( None )
