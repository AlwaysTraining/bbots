from HTML import Table
from HTML import TableCell
from Queue import Queue
from subprocess import Popen
from subprocess import PIPE

import bbot.botlog
import bbot.Utils
import traceback
import time
import logging


DEFAULT_REFRESH_TIME = 60
FAST_REFRESH_TIME = 10

class WebUi:


    def __init__(self, con):
        self.header = [ 'status','id','realm','address','last_attempt' ]
        self.con = con
        self.history_table_data = []
        self.refresh_time = DEFAULT_REFRESH_TIME
        self.weblogfile = None
        self.bbotslogfile = None

    def on_game_in_progress(self, rec):
        ui_row=[]
        for header_col in self.header:
            if header_col in rec:
                ui_row.append(rec[header_col])
        self.history_table_data.append(ui_row)
        self.refresh_time = FAST_REFRESH_TIME
        return len(self.history_table_data) - 1

    def on_update_ui_row(self, which_row, rec):
        ui_row = self.history_table_data[which_row]
        self.refresh_time = DEFAULT_REFRESH_TIME
        for header_col_index in range(len(self.header)):
            header_col = self.header[header_col_index]
            if header_col in rec:
                ui_row[header_col_index] = rec[header_col]


#     def graphs(self):
#         return (
# """
# <body>
# <script type="text/javascript" src="//ajax.googleapis.com/ajax/static/modules/gviz/1.0/chart.js">
# {"dataSourceUrl":"//docs.google.com/spreadsheet/tq?key=0AlItClzrqP_edHoxMmlOcTV3NHJTbU4wZDJGQXVTTXc&transpose=0&headers=1&range=A1%3AB9&gid=9&pub=1","options":{"titleTextStyle":{"bold":true,"color":"#000","fontSize":16},"series":{"0":{"color":"#ff0000"}},"animation":{"duration":500},"width":600,"hAxis":{"useFormatFromData":true,"slantedTextAngle":30,"slantedText":true,"minValue":null,"viewWindowMode":null,"textStyle":{"color":"#222","fontSize":"12"},"viewWindow":null,"maxValue":null},"vAxes":[{"title":null,"useFormatFromData":true,"minValue":null,"viewWindow":{"min":null,"max":null},"maxValue":null},{"useFormatFromData":true,"minValue":null,"viewWindow":{"min":null,"max":null},"maxValue":null}],"booleanRole":"certainty","title":"Scores","height":371,"legend":"right","focusTarget":"series","isStacked":false,"tooltip":{}},"state":{},"view":{},"isDefaultVisualization":false,"chartType":"ColumnChart","chartName":"Chart 1"}
# </script></body>
# """)
#     graphs.exposed = True


    def botdash(self):
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
            cmd = "$(which tail) -n 50 " + str(bbot.botlog.logfilepath)
            output = Popen(cmd, stdout=PIPE, shell=True).communicate()[0]
            html.append(output)
            html.append("</pre>")

        html.append(str(history_table))
        html.append("</body>")
        return ''.join(html)


    botdash.exposed = True

    def log_page(self,filepath):

        html = []
        html.append("<head>")
        html.append('<meta http-equiv="Refresh" content="' + 
                str(60) +'">')
        html.append("</head>")
        html.append("<body>")

        if self.bbotslogfile is None:
            html.append("No log file set")
        else:

            html.append("<pre>")
            cmd = "$(which tail) -n 1000 " + str(filepath)
            output = Popen(cmd, stdout=PIPE, shell=True).communicate()[0]
            html.append(output)
            html.append("</pre>")

        html.append("</body>")
        return ''.join(html)

    def botlog(self):
        return self.log_page(self.bbotslogfile)
    botlog.exposed = True

    def weblog(self):
        return self.log_page(self.weblogfile)
    weblog.exposed = True

    def botstats(self):
        try:

            start = time.time()
            sskey = self.con.data.get_sskey()
            self.con.data.process_stats(sskey=sskey,cols=self.con.stats_cols)
            return ("<body><pre>Success in " +
                str(time.time() - start) +
                " seconds</pre></body>")
        except:
            return "<body><pre>" + traceback.format_exc() + "</pre></body>"
    botstats.exposed = True

    def botgraph(self):
        html = []
        self.con.data.load_ss(['server'])
        html.append('<body>')
        html.append(self.con.data.chart_html)
        html.append('</body>')
        return ''.join(html)
    botgraph.exposed = True

    def get_app_value(self,key,secret=False):
        return self.con.data.get_app_value(key,secret)

    def botstatusmail(self):
        html = []
        self.con.data.load_ss(['server'])


        to = self.get_app_value('notify')
        if isinstance(to, basestring):
            to = [to]

        logging.info("Sending Status email to " + str(to))

        files = []

        subject = "Status Mail"

        body = "----====----\n"
        body = "bbots status\n"
        body = "----====----\n\n"

        try:

            start = time.time()
            sskey = self.con.data.get_sskey()
            self.con.data.process_stats(sskey=sskey, cols=self.con.stats_cols)
            body += ("Stats recalculated in " +
                    str( round(time.time() - start) / 60.0,1) +
                    " minutes\n\n")
        except:
            body += ("Stats calculation failed in " +
                     str(round(time.time() - start) / 60.0, 1) +
                     " minutes\n\n" +
                     traceback.format_exc() + "\n\n")

        body += self.con.data.chart_html

        bbot.Utils.send_mail(
            to,
            '[bbots] ' + subject,
            body,
            _from=self.get_app_value('smtp_user'),
            files=files,
            server=self.get_app_value('smtp_server'),
            port=self.get_app_value('smtp_port'),
            server_user=self.get_app_value('smtp_user'),
            server_user_pass=self.get_app_value('smtp_password',secret=True))




    botgraph.exposed = True



