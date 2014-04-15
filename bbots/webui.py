from HTML import Table
from HTML import TableCell
from Queue import Queue
from subprocess import Popen
from subprocess import PIPE

import bbot.botlog
import traceback


DEFAULT_REFRESH_TIME = 60*60

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
        self.refresh_time = 1
        return len(self.history_table_data) - 1

    def on_update_ui_row(self, which_row, rec):
        ui_row = self.history_table_data[which_row]
        self.refresh_time = DEFAULT_REFRESH_TIME
        for header_col_index in range(len(self.header)):
            header_col = self.header[header_col_index]
            if header_col in rec:
                ui_row[header_col_index] = rec[header_col]


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
            self.con.data.process_stats()
            return "<body><pre>Success</pre></body>"
        except:
            return "<body><pre>" + traceback.format_exc() + "</pre></body>"
    botstats.exposed = True

    def addrow(self):
        try:
            d = {'pop-support-bribe': '1899750', 'gold': '0',
                 'food-units': '2755746',
                 'smtp-password': 'dr.randy.myers.password',
                 'army-headquarters-price': '41531',
                 'advisors-economic-menu-option': '2',
                 'smtp-server': 'smtp.gmail.com',
                 'regions-industrial-zonemanufacturing-turrets-menu-option': '3',
                 'regions-industrial-zonemanufacturing-carriers-menu-option': '9',
                 'regions-technology-menu-option': 't',
                 'regions-industrial-zonemanufacturing-carriers-allocation': '0',
                 'army-carriers-price': '5303', 'army-tanks-number': '4434527',
                 'regions-industrial-zonemanufacturing-turrets-allocation': '100',
                 'regions-number': '17720', 'food-menu-option': '5',
                 'game': '6', 'population-pop-support': '54',
                 'password': 'karpet', 'name': 'Skull House',
                 'hour-delay-from-midnight-to-first-play': '9',
                 'regions-industrial-zonemanufacturing-tanks-production': '0',
                 'army-agents-menu-option': '7',
                 'regions-industrial-zonemanufacturing-troopers-production': '0',
                 'debug': 'False',
                 'regions-industrial-zonemanufacturing-bombers-menu-option': '4',
                 'army-jets-number': '19',
                 'regions-industrial-zonemanufacturing-troopers-num-per-carrier': '1000',
                 'regions-industrial-zonemanufacturing-jets-menu-option': '2',
                 'regions-industrial-zonemanufacturing-turrets-num-per-carrier': '1000',
                 'regions-mountain-earnings': '10061793',
                 'LocalLackey-trade-items': 'Tanks, Agents',
                 'regions-urban-menu-option': 'u',
                 'regions-coastal-earnings': '119020',
                 'army-troopers-menu-option': '1', 'population-size': '42050',
                 'regions-maintenance': '15426657',
                 'regions-industrial-zonemanufacturing-troopers-menu-option': '1',
                 'population-food': '63075',
                 'last-attempt': '2014-04-12 23:10:00.252622',
                 'regions-industrial-zonemanufacturing-bombers-allocation': '0',
                 'bank-gold': '196227471',
                 'regions-agricultural-foodyield': '139194',
                 'regions-river-menu-option': 'r',
                 'army-turrets-menu-option': '3',
                 'army-headquarters-menu-option': '5',
                 'address': 'tnsoa.strangled.net',
                 'population-taxearnings': '1251402',
                 'army-troopers-price': '283',
                 'LocalLackey-master': 'Death Star',
                 'LocalLackey-tribute-ratio': '1', 'successes': '42',
                 'regions-industrial-zonemanufacturing-troopers-allocation': '0',
                 'army-carriers-number': '0', 'turns-remaining': '2',
                 'last-completed-all-turns': '2014-04-10 16:20:37',
                 'army-tanks-price': '1637', 'army-jets-price': '305',
                 'regions-industrial-zonemanufacturing-bombers-production': '0',
                 'army-maintenance': '4105574',
                 'army-carriers-menu-option': '9',
                 'regions-desert-earnings': '1298986',
                 'army-tanks-menu-option': '8',
                 'army-turrets-number': '1590698',
                 'advisors-military-menu-option': '3',
                 'notify': 'derrick.karimi@gmail.com,mrkauffman@gmail.com',
                 'turnsplit': '1', 'regions-agricultural-menu-option': 'a',
                 'turns-years-freedom': '464', 'queen-taxes': '1349507',
                 'army-bombers-number': '0', 'army-jets-menu-option': '2',
                 'regions-industrial-zonemanufacturing-jets-allocation': '0',
                 'army-agents-price': '10364', 'army-agents-number': '63256',
                 'population-growth': '1558', 'username': 'Bob Falooley',
                 'regions-industrial-zonemanufacturing-jets-production': '0',
                 'food-spoilage': '88422', 'bank-investments': '[]',
                 'army-troopers-num-per-carrier': '1000',
                 'regions-industrial-zonemanufacturing-tanks-menu-option': '8',
                 'regions-industrial-zonemanufacturing-tanks-allocation': '0',
                 'army-bombers-price': '3725', 'enabled': 'True',
                 'army-headquarters-number': '0',
                 'strategies': 'AgentRecruiter',
                 'army-tanks-num-per-carrier': '5000',
                 'regions-industrial-zonemanufacturing-jets-num-per-carrier': '100',
                 'smtp-user': 'dr.randy.myers',
                 'advisors-civilian-menu-option': '1',
                 'regions-industrial-zonemanufacturing-tanks-num-per-carrier': '5000',
                 'id': 'tnsoa3', 'army-turrets-price': '391',
                 'realm': 'Skull House', 'regions-number-affordable': '0',
                 'population-rate': '15',
                 'regions-industrial-zonemanufacturing-turrets-production': '230520',
                 'regions-industrial-zonemanufacturing-carriers-production': '0',
                 'regions-price': '1205894',
                 'advisors-technology-menu-option': '4',
                 'army-troopers-number': '33019', 'status': 'success',
                 'smtp-port': '587', 'regions-menu-option': '6',
                 'army-turrets-num-per-carrier': '1000',
                 'regions-industrial-menu-option': 'i', 'turns-score': '188168',
                 'failures': '7', 'army-bombers-menu-option': '4',
                 'army-jets-num-per-carrier': '100', 'turns-current': '3',
                 'army-food': '767'}

            self.con.data.append_data_sheet_row(d)
            return "<body><pre>Success</pre></body>"
        except:
            return "<body><pre>" + traceback.format_exc() + "</pre></body>"

    addrow.exposed = True


