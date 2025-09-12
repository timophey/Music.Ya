import npyscreen
from collections import OrderedDict
from tui_common_form import TuiCommonForm

class TuiCommonTableForm(TuiCommonForm):

    # table
    list_data = []
    list_total = 0
    list_height = 0
    list_start = 0
    list_end = 0
    list_pos = 0
    list_item = None

    # help
    help_strings = []

    def create( self ):
        super().create()
        # make widgets
        self.list_header = self.add(npyscreen.FixedText, value="/", color="IMPORTANT", editable=False)
        self.list_widget = self.add(npyscreen.MultiLine, values=[], max_height=-4, scroll_exit=True)
        self.list_status = self.add(npyscreen.FixedText, value="...", editable=False)
        # bind scroll
        self.list_widget.when_cursor_moved = self.on_scroll
        # bind help
        y, x = self.useable_space()
        self.help_widget = self.add( npyscreen.BoxTitle, name="Help", values = self.help_strings, relx=x//4, rely=y//4, max_height=y//2, max_width=x//2, editable=False, hidden=True)
        self.add_handlers({
            "h": self.toggle_help
        })

    def get_list( self ):
        return list_data

    # when form opened
    def beforeEditing(self):
        # for example
        # self.spinner_widget.start()
        # time.sleep(2)
        # self.spinner_widget.stop()
        self.refresh_display()

    def refresh_display( self, from_db = True ):
        try:
            data_list = self.get_list() # if from_db else list_data
            data_columns = self.get_columns()
            data_column_widths = self.get_column_widths()
            data_lines = self.format_table(data_list, data_columns, data_column_widths)

            self.list_widget.values = data_lines
            self.list_widget.display()

            self.refresh_status()


        except Exception as e:
            self.list_widget.values = [f"Error: {str(e)}"]
            # self.status.value = "Ошибка загрузки"
            # self.status.display()

    def refresh_status( self ):
        self.list_total = len(self.list_widget.values)
        self.list_height = self.list_widget.height
        self.list_start = getattr(self.list_widget, 'start_display_at', 0)
        self.list_end = min(self.list_start + self.list_height, self.list_total)
        self.list_pos = self.list_widget.cursor_line
        self.list_item = self.list_data[self.list_pos]
        # if self.list_total > 0:
        self.list_status.value = f"L {self.list_start+1}+{self.list_pos} {self.list_start+1+self.list_pos}/{self.list_total} ({self.list_height}ipp)"
        
        
        self.list_status.display()
        
    def on_scroll( self ):
        self.refresh_status()

    def get_columns( self ):
        return list(OrderedDict.fromkeys(key for d in self.list_data for key in d))
    def get_column_widths( self ):
        return []

    def format_table(self, data, keys, col_widths):
        lines = []

        if not keys:
            # Нет столбцов — заголовок и строки пустые
            self.list_header.value = ''
            return lines

        # Вычисляем ширину каждого столбца
        adjusted_widths = []
        for i, key in enumerate(keys):
            # Максимальная длина заголовка
            max_len = len(str(key))
            # Максимальная длина среди значений этого столбца
            for row in data:
                value_len = len(str(row.get(key, '')))
                if value_len > max_len:
                    max_len = value_len

            # Если передан col_widths, используем его значение как максимум
            if col_widths and i < len(col_widths):
                col_max = col_widths[i]
                # Ограничиваем ширину столбца col_max
                adjusted_widths.append(min(max_len, col_max))
            else:
                # Если col_widths пуст, просто используем максимум
                adjusted_widths.append(max_len)

        # Формируем строку заголовка с учетом ширин столбцов
        header_cells = [str(k)[:w].ljust(w) for k, w in zip(keys, adjusted_widths)]
        header_line = ' | '.join(header_cells)
        self.list_header.value = header_line

        # Формируем строки таблицы с учетом ширин
        for row in data:
            cells = [str(row.get(key, ''))[:w].ljust(w) for key, w in zip(keys, adjusted_widths)]
            line = ' | '.join(cells)
            lines.append(line)

        return lines

    ##
    # Help
    ##

    def toggle_help(self, _input):
        # Переключаем видимость справки
        self.help_widget.hidden = not self.help_widget.hidden
        self.help_widget.display()
        self.display()  # обновить основную форму
        if self.help_widget.hidden:
            self.refresh_display()

