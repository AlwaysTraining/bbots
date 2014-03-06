from HTML import Table
from HTML import TableCell
from Queue import Queue
from subprocess import Popen
from subprocess import PIPE
import bbot.botlog


DEFAULT_REFRESH_TIME = 60*60

class WebUi:


    def __init__(self):
        self.header = [ 'status','id','realm','address','last_attempt' ]
        self.history_table_data = []
        self.refresh_time = DEFAULT_REFRESH_TIME
    def on_game_in_progress(self, rec):
        ui_row=[]
        for header_col in self.header:
            if header_col in rec:
                ui_row.append(rec[header_col])
        self.history_table_data.append(ui_row)
        self.refresh_time = 1
        return len(self.history_table_data) - 1

    def on_update_ui_row(self, which_row, rec):
        ui_row = self.history_table_data[which_row]
        self.refresh_time = DEFAULT_REFRESH_TIME
        for header_col_index in range(len(self.header)):
            header_col = self.header[header_col_index]
            if header_col in rec:
                ui_row[header_col_index] = rec[header_col]


    def index(self):
        history_table = Table(header_row=self.header)
        for table_data_row in reversed(self.history_table_data):
            history_row = []
            for colindex in range(len(table_data_row)):
                colname = self.header[colindex]
                colvalue = table_data_row[colindex]
                color = 'White'
                if colname == 'status':
                    if colvalue == 'in progress':
                        color = 'Yellow'
                    elif colvalue == 'success':
                        color = 'Green'
                    else:
                        color = 'Red'

                history_row.append(TableCell(colvalue,bgcolor=color))
            history_table.rows.append(history_row)

        html = []
        html.append("<head>")
        html.append('<meta http-equiv="Refresh" content="' + 
                str(self.refresh_time) +'">')
        html.append("</head>")
        html.append("<body>")

        if bbot.botlog.tracefilepath is not None:
            html.append("<pre>")
            cmd = "$(which tail) -n 50 " + str(bbot.botlog.tracefilepath)
            output = Popen(cmd, stdout=PIPE, shell=True).communicate()[0]
            html.append(output)
            html.append("</pre>")

        html.append(str(history_table))
        html.append("</body>")
        return ''.join(html)


    index.exposed = True
