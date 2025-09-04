import threading
import time
import os
import re

import npyscreen

import textwrap
import pprint

class FavoritesBaseForm(npyscreen.ActionForm):

    spinner_running = False

    def __init__(self, *args, favorite_module=None, **kwargs):
        # super().__init__(*args, **kwargs)
        self.favorite_module = favorite_module
        super().__init__(*args, **kwargs)

    def create(self):
        
        self.spinner_widget = self.add(npyscreen.FixedText, value="Готов...", editable=False)

        self.list_header = self.add(npyscreen.FixedText, value="/", color="IMPORTANT")
        self.list_widget = self.add(npyscreen.MultiLine, values=[], max_height=-4, scroll_exit=True)
        self.list_widget.when_cursor_moved = self.on_scroll
        self.status = self.add(npyscreen.FixedText, value="Статус: готов")
        self.hotkeys = self.add(npyscreen.FixedText, value="Горячие клавиши: Ctrl+S — Синхронизация | Esc — Назад | i - load info | p  - show path | d - download")
        self.debug_widget = self.add(npyscreen.FixedText, value="Отладка:")
        self.add_handlers({"^S": self.sync_data})
        if hasattr(self.favorite_module, 'bind'):
            self.favorite_module.bind(self)
        if hasattr(self.favorite_module, 'current_parent'):
            self.favorite_module.current_parent = self

    def spinner_loop(self):
        spinner_sequence = ['|', '/', '-', '\\']
        i = 0
        while self.spinner_running:
            self.spinner_widget.value = f"Загрузка данных... {spinner_sequence[i % len(spinner_sequence)]} "
            self.spinner_widget.display()
            i += 1
            time.sleep(0.1)
        self.spinner_widget.value = "Загрузка завершена.          "
        self.spinner_widget.display()

    def start_spinner(self):
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=self.spinner_loop, daemon=True)
        self.spinner_thread.start()

    def stop_spinner(self):
        self.spinner_running = False
        if hasattr(self, 'spinner_thread'):
            self.spinner_thread.join()

    def beforeEditing(self):
        # self.start_spinner()
        # threading.Thread(target=self.load_data_and_update, daemon=True).start()
        self.refresh_display()
        if hasattr(self.favorite_module, 'on_ready'):
            self.favorite_module.on_ready()

    def format_cell_text(self, text, width):
        return '\n'.join(textwrap.wrap(text, width=width))

    def format_table(self, data, keys, col_widths):
        lines = []

        # Вычисляем минимальную ширину каждого столбца с учётом заголовков
        adjusted_widths = [max(len(str(k)), w) for k, w in zip(keys, col_widths)]
        adjusted_widths = [
            min(max(len(str(k)), w), w)  # max длина между заголовком и 0, но максимально w
            for k, w in zip(keys, col_widths)
        ]

        # Формируем строку заголовка с учетом ширин столбцов
        header_cells = [str(key)[:w].ljust(w) for key, w in zip(keys, adjusted_widths)]
        header_line = ' | '.join(header_cells)
        self.list_header.value = header_line

        # Заголовок — без переноса
        # headers = keys
        # header_line = ' | '.join(h.ljust(w) for h, w in zip(headers, col_widths))
        # lines.append(header_line)
        # lines.append('-' * (sum(col_widths) + 3 * (len(col_widths) - 1)))

        for row in data:
            # cells = [str(getattr(row, key, '')) for key in keys]
            cells = [str(row.get(key, '')) for key in keys]
            # Обрезаем текст по ширине без переноса
            cells_trimmed = [c[:w].ljust(w) for c, w in zip(cells, adjusted_widths)]
            line = ' | '.join(cells_trimmed)
            lines.append(line)
        return lines



    def refresh_display(self):
        try:
            data_list = self.favorite_module.get_from_db()
            
            # display_list = [str(item) for item in data_list]
            col_widths = [10, 20]
            
            table_columns = self.favorite_module.get_table_columns()
            col_widths = self.favorite_module.get_table_widths()
            # table_lines = self.format_table(data_list, table_columns, col_widths)
            table_lines = self.format_table(data_list, table_columns, col_widths)
            
            
            # self.debug_widget.value = pprint.pformat(data_list[0])
            # self.debug_widget.display()

            # print(data_list[0])

            # self.list_widget.values = table_lines
            self.list_widget.values = table_lines
            self.update_status()
            self.list_widget.display()
        except Exception as e:
            self.list_widget.values = [f"Ошибка: {str(e)}"]
            self.status.value = "Ошибка загрузки"
            self.status.display()


    def on_scroll(self):
        if hasattr(self.favorite_module, 'current_position'):
            self.favorite_module.current_position = self.list_widget.cursor_line
        if hasattr(self.favorite_module, 'current_list_limit'):
            self.favorite_module.current_list_limit = self.list_widget.height
        if hasattr(self.favorite_module, 'on_scroll'):
            self.favorite_module.on_scroll()
        self.refresh_display()

    def update_status(self):
        total = len(self.list_widget.values)
        visible_count = self.list_widget.height
        start = getattr(self.list_widget, 'start_display_at', 0)
        end = min(start + visible_count, total)
        pos = self.favorite_module.current_position
        if total > 0:
            self.status.value = f"Загружено {start+1}-{end-1} ({visible_count}) из {total} элементов / {pos+1}"
        else:
            self.status.value = "Список пуст"
        self.status.display()

    def update_list(self):
        try:
            self.refresh_display()
        except Exception as e:
            self.list_widget.values = [f"Ошибка загрузки: {str(e)}"]
            self.status.value = "Ошибка"
        self.display()


    def sync_data(self, *args, **kwargs):
        self.start_spinner()
        self.status.value = "Синхронизация..."
        self.display()

        def sync_and_update():
            self.favorite_module.sync_from_api()
            self.stop_spinner()
            self.update_list()
            self.status.value = "Синхронизировано"
            self.refresh_display()
            # self.display()

        threading.Thread(target=sync_and_update, daemon=True).start()

        

    def on_ok(self):
        self.parentApp.setNextForm('MAIN')
        self.editing = False

    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')
        self.editing = False
