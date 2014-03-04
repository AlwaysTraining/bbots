from HTML import Table
from Queue import Queue

class WebUi:


    def __init__(self):
        self.header = [ 'status','id','realm','address','last_attempt' ]
        self.history_table_data = []
    def on_game_in_progress(self, rec):
        ui_row=[]
        for header_col in self.header:
            if header_col in rec:
                ui_row.append(rec[header_col])
        self.history_table_data.append(ui_row)
        return len(self.history_table_data) - 1

    def on_update_ui_row(self, which_row, rec):
        ui_row = self.history_table_data[which_row]
        for header_col_index in range(len(self.header)):
            header_col = self.header[header_col_index]
            if header_col in rec:
                ui_row[header_col_index] = rec[header_col]


    def index(self):
        history_table = Table(header_row=self.header)
        for table_row in self.history_table_data:
            history_table.rows.append(table_row)

        return str(history_table)


    index.exposed = True
