import npyscreen
import threading
import time

class WidgetSpinner():

    running = False
    
    def __init__(self, form, ready = "Ready", loading = "Loading"):
        self.form = form
        self.ready = ready
        self.loading = loading
        self.widget = self.form.add(npyscreen.FixedText, value=ready, editable=False)
        # self.spinner_widget = self.add(npyscreen.FixedText, value="Готов...", editable=False)

    def start( self ):
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop( self ):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def loop( self ):
        i = 0
        spinner_sequence = ['|', '/', '-', '\\']
        while self.running:
            self.widget.value = f"{self.loading}... {spinner_sequence[i % len(spinner_sequence)]} "
            self.widget.display()
            i += 1
            time.sleep(0.1)
        self.widget.value = self.ready
        self.widget.display()


        