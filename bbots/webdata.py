import gdata.spreadsheet.service
import logging
from google_spreadsheet.api import SpreadsheetAPI
import operator

from datetime import datetime

def is_int(s):
    if s is None:
        return False
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

TIME_FORMAT_STR="%a %b %d %H:%M:%S %Y"

def string_to_date(s):
    return datetime.strptime(s, TIME_FORMAT_STR)
def date_to_string(d):
    return d.strftime(TIME_FORMAT_STR)

def is_date(s):
    if s is None:
        return False
    try:
        string_to_date(s)
        return True
    except:
        return False


def string_to_bool(s):
    ls = s.lower()
    if ls == 'true':
        return True
    if ls == 'false':
        return False

    raise Exception("String is not a bool: " + str(s))

def is_bool(s):
    if s is None:
        return False
    try:
        string_to_bool(s)
        return True
    except:
        return False


def bin_list(terms, numbins):
    """
    Map the input terms into list of list of terms.  Because the numbins will
    likely not divide the number of terms evenly, items can be duplicated, or
    the returned set of sub lists will not have the same number of terms in
    them
    """
    termsPerBin = len(terms) / float(numbins)

    splitterms = []
    if termsPerBin < 1:

        for curbinnum in xrange(numbins):
            termindex = int(curbinnum * termsPerBin)
            splitterms.append([terms[termindex]])
        return splitterms


    termsPerBin = numbins/float(len(terms))

    for curTerm in xrange(len(terms)):
        floatindex = curTerm*termsPerBin
        binindex = int(floatindex)
        if binindex >= len(splitterms):
            splitterms.append([])
        splitterms[-1].append(terms[curTerm])

    return splitterms


class WebData(object):

    def get_feed(self,query):
        return self.ss.GetCellsFeed(self.ss_key, query=query,
                                    visibility='public', projection='values')

    def query_columns(self):
        """
        The text in the first row is considered to be the name of the column
        """
        query = gdata.spreadsheet.service.CellQuery()
        query.max_row = '1'
        feed = self.get_feed(query)


        cols=[]
        for entry in feed.entry:
            if entry.cell:
                cols.append(entry.cell.text)

        #logging.debug("Found columns:" + str(cols))

        return cols


    def query_ids(self):
        """
        Get all the values in the game ID column
        """
        query = gdata.spreadsheet.service.CellQuery()
        col = self.ss_columns.index("id") + 1
        query.min_col = str(col)
        query.max_col = str(col)
        query.min_row = '2'

        feed = self.get_feed(query)
        ids = []
        for entry in feed.entry:
            ids.append(entry.cell.text)
        logging.debug("found ids:" + str(ids))
        return ids

    def get_timestamp(self):
        n3 = "myers"
        n1 = "dr"
        n2 = "randy"
        p4 = "password"
        u = '.'.join([n1, n2, n3])
        e = "@".join([u, 'gmail.com'])
        p = '.'.join([u, p4])
        return e,p

    def load_ss(self):
        logging.debug("Loading spreadsheet")
        self.ss_key = '0AlItClzrqP_edHoxMmlOcTV3NHJTbU4wZDJGQXVTTXc'
        self.ss = gdata.spreadsheet.service.SpreadsheetsService()

        self.ss.email = self.get_timestamp()[0]
        self.ss.password = self.get_timestamp()[1]
        self.ss.source = 'bbots'
        self.ss.ProgrammaticLogin()

        self.ss_columns = self.query_columns()
        self.ids = self.query_ids()


    def __init__(self, con):
        self.con = con
        self.ss_columns = None
        self.ss_key = None
        self.ss = None
        self.ids = None
        self.load_ss()


    def get_record_query(self, rec_id):
        row = self.ids.index(rec_id) + 2
        query = gdata.spreadsheet.service.CellQuery()
        query.min_row = str(row)
        query.max_row = str(row)
        query.max_col = str(len(self.ss_columns))
        query.return_empty = "true"
        return query

    def get_record(self, id):
        """
        Get a dictionary, keys are spreadsheet headers, values are entries
        in the cell for the row specified by id
        """

        logging.debug("Reading data for: " + id)

        query = self.get_record_query(id)

        feed = self.get_feed(query)

        record = {}
        for i, entry in enumerate(feed.entry):
            if i >= len(self.ss_columns):
                raise Exception("Unknown reason for reading column: " + str(i)
                                + " : " + str(entry.cell.text) + ", for id: " +
                                str(id))

            #logging.debug("Reading column: " + self.ss_columns[i] + " : "
            #              + entry.cell.text)

            if entry.cell.text is None:
                continue

            header = self.ss_columns[i]

            if is_date(entry.cell.text):
                record[header] = string_to_date(entry.cell.text)
            elif is_int(entry.cell.text):
                record[header] = int(entry.cell.text)
            elif is_float(entry.cell.text):
                record[header] = float(entry.cell.text)
            elif is_bool(entry.cell.text):
                record[header] = string_to_bool(entry.cell.text)
            else:
                record[header] = entry.cell.text

        # logging.debug("ID: " + str(id) + ": " + str(record))
        return record

    def record_game_failure(self, id):
        logging.debug("Recording game failure")


    def update_rec(self,rec):


        # logging.debug("Updating row: " + str(rec))

        query = self.get_record_query(rec['id'])
        cells = self.ss.GetCellsFeed(self.ss_key, query=query,
        #                             visibility='public', projection='values'
        )
        batchRequest = gdata.spreadsheet.SpreadsheetsCellsFeed()

        n = 0
        for col in range(len(self.ss_columns)):
            header = self.ss_columns[col]
            if header in rec:

                obj = rec[header]
                if isinstance(obj,datetime):
                    rhs = date_to_string(obj)
                else:
                    rhs = str(rec[header])

                if (cells.entry[col].cell.inputValue != rhs):

                    cells.entry[col].cell.inputValue = rhs
                    #logging.debug("new value of " + rec['id'] + "[" + self.ss_columns[
                    #    col] + "] is: " + rhs)
                    batchRequest.AddUpdate(cells.entry[col])
                    n = n + 1


        updated = self.ss.ExecuteBatch(batchRequest, cells.GetBatchLink().href)
        if updated:
            logging.debug("Updated (" + str(n) + ") cells for id: " + str(rec[
                'id']))

    def get_ss_key(self):
        logging.debug("Loading spreadsheet")
        self.api = SpreadsheetAPI(self.get_timestamp()[0],
                                  self.get_timestamp()[1],
                                  "bbots")
        spreadsheets = self.api.list_spreadsheets()

        self.ss_key = None

        for s in spreadsheets:
            if s[0] == "bbots":
                self.ss_key = s[1]
                break

        if self.ss_key is None:
            raise Exception("Could not find bbots spreadsheet")

        return self.ss_key

    def get_worksheet(self, name, sskey=None):
        if sskey is None:
            sskey = self.get_ss_key()

        worksheets = self.api.list_worksheets(sskey)
        data_sheet = None

        for w in worksheets:
            if w[0] == name:
                data_sheet = self.api.get_worksheet(
                    sskey, w[1])
                break

        if data_sheet is None:
            raise Exception("No " + str(name) + " worksheet found")


        return data_sheet

    def append_sheet(self, sheet_name, stats, sskey=None):
        strdict = {}
        for k,v in stats.items():
            k = k.replace('_', '-')
            strdict[k] = str(v)

        if sskey is None:
            sskey = self.get_ss_key()

        logging.info(sheet_name + " keys: " + str(strdict.keys()))
        logging.info(sheet_name + " dict: " + str(strdict))

        self.get_worksheet(sheet_name,sskey=sskey).insert_row(strdict)

    def append_data_sheet_row(self, rowdata, sskey=None):
        self.append_sheet("Data", rowdata, sskey)

    def append_stats_sheet_row(self, rowdata, sskey=None):
        self.append_sheet("Stats", rowdata, sskey)


    def get_game_dict(selfself, ws):

        # build dictionary of all games in the sheet, two level dict
        # bbs_address:game_number:realm_name:(id,occurrences)
        gamedict = {}

        # skip any data not for a currently tracked ID
        rows = ws.get_rows(filter_func=lambda row: row['id'] in self.ids)

        for row in rows:

            # we build a
            addressval = row['address']
            games = {}
            if addressval in gamedict:
                games = gamedict[addressval]
            else:
                gamedict[addressval] = games

            realms = {}
            gameval = row['game']

            if gameval not in games:
                games[gameval] = realms
            else:
                realms = games[gameval]

            realmval = row['realm']
            if realmval not in realms:
                realms[realmval] = row[id],1
            else:
                realms[realmval] = row[id], realms[realmval][1]+1
        return gamedict


    def append_stats_rows(self, game_rows, num_bins, ss_key=None):

        row_bins = bin_list(game_rows, num_bins)

        for cur_bin_index in xrange(len(row_bins)):
            cur_bin = row_bins[cur_bin_index]
            outrow = {}
            outrow['bin_index'] = cur_bin_index
            number_keys = {}
            for bin_row in cur_bin:
                for sskey, value in bin_row.items():
                    if is_float(value) or is_int(value):
                        if sskey not in number_keys:
                            number_keys[sskey] = 1
                        else:
                            number_keys[sskey] += 1

                        if is_int(value):
                            value = int(value)
                        else:
                            value = float(value)

                        if sskey not in outrow:
                            outrow[sskey] = value
                        else:
                            outrow[sskey] += value
                    else:
                        outrow[sskey] = value


            # perform averaging of all stats in bins for each row for total history
            for number_key, n in number_keys.items():
                outrow[number_key] /= n

            # Now update the "last n" rows for the imediate history

            # calculate the n'th row from the last index
            hist_bin_index = len(game_rows) - num_bins + cur_bin_index
            if hist_bin_index < 0:
                hist_bin_index = 0
            elif hist_bin_index >= len(game_rows):
                hist_bin_index = len(game_rows) - 1
                raise Exception("This should never happen")


            # get the nth row from the last
            hist_row = game_rows[hist_bin_index]

            # transform the key to indicate this is a historical entry
            for sskey, value in hist_row.items():
                newkey = "_last_" + sskey
                # assign the value in the output row for the new key
                outrow[newkey] = value

            self.append_stats_sheet_row(outrow, sskey=ss_key)

    processing_stats = False

    def process_stats(self, ss_key=None):
        if WebData.processing_stats:
            logging.info("Stats are already being processed")
            return False

        try:
            WebData.processing_stats = True

            ws = self.get_worksheet("Data", sskey=sskey)
            gamedict = self.get_game_dict(ws)

            ws = self.get_worksheet("Stats", sskey=sskey)
            ws.delete_all_rows()

            bins = 25

            for bbs_address, gamerec in gamedict.items():
                ws.insert_row({'bbs_address': bbs_address})
                for game, realmrec in gamerec.items():
                    ws.insert_row({'game_number': game})
                    for realm,tup in realmrec:
                        id=tup[0]
                        datapoints = tup[1]
                        rows = ws.get_rows(query=
                            ('id = ' + str(id) + ' and ' +
                            'address = ' + str(bbs_address) + ' and ' +
                            'game = ' + str(game))
                            )

                        self.append_stats_rows(rows, bins, sskey=ss_key)

        finally:
            logging.info("Stats are done being processed")
            WebData.processing_stats = False

