import gdata.spreadsheet.service
import logging
from google_spreadsheet.api import SpreadsheetAPI
from pprint import pformat
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

    logging.debug("There are " + str(termsPerBin)  + " terms per stats bin")

    splitterms = []
    if termsPerBin < 1:

        for curbinnum in xrange(numbins):
            termindex = int(curbinnum * termsPerBin)
            if termindex >= len(terms):
                raise Exception("For stats bin: " + str(curbinnum) +
                                ", we calculated a term index: " +
                                str(termindex) + ", but there are only " +
                                str(len(terms)) + " terms")

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
        return self.ss.GetCellsFeed(self.sskey, query=query)
                                    # visibility='public', projection='values')

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

    def load_ss(self,sheets=None):
        sskey = self.get_sskey()
        # self.sskey = '0AlItClzrqP_edHoxMmlOcTV3NHJTbU4wZDJGQXVTTXc'
        self.ss = gdata.spreadsheet.service.SpreadsheetsService()

        self.ss.email = self.get_timestamp()[0]
        self.ss.password = self.get_timestamp()[1]
        self.ss.source = 'bbots'
        logging.info("Logging in to gdocs")
        self.ss.ProgrammaticLogin()

        if sheets is None or 'games' in sheets:
            self.ss_columns = self.query_columns()
            self.ids = self.query_ids()

        if sheets is None or 'server' in sheets:
            serverSheet = self.get_worksheet('server',sskey)
            serverRows = serverSheet.get_rows()
            chartCol = []
            self.firstServerRow = None
            for r in serverRows:
                if self.firstServerRow is None:
                    self.firstServerRow = r
                logging.info("Server row: " + str(r))
                if ('charts' in r):
                    chartCol.append(r['charts'])
            self.chart_html = '\n'.join(chartCol)

        logging.info("Spreadsheet Loaded")



    def __init__(self, con):
        self.con = con
        self.ss_columns = None
        self.sskey = None
        self.ss = None
        self.ids = None
        self.firstServerRow = None
        self.chart_html = ''
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
        cells = self.ss.GetCellsFeed(self.sskey, query=query,
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

    def get_sskey(self):
        logging.debug("Loading spreadsheet")
        self.api = SpreadsheetAPI(self.get_timestamp()[0],
                                  self.get_timestamp()[1],
                                  "bbots")
        spreadsheets = self.api.list_spreadsheets()

        self.sskey = None

        for s in spreadsheets:
            if s[0] == "bbots":
                self.sskey = s[1]
                break

        if self.sskey is None:
            raise Exception("Could not find bbots spreadsheet")

        return self.sskey

    def get_worksheet(self, name, sskey=None):
        if sskey is None:
            sskey = self.get_sskey()

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

    def get_tabbed_list_str(self, col):
        col = list(col)
        col.sort()
        keystr = str(col)
        keystr = keystr.replace("'", '')
        keystr = keystr.replace(', ', '\t')
        return keystr

    def append_sheet(self, sheet_name, stats, sskey=None):
        strdict = {}
        for k,v in stats.items():
            k = k.replace('_', '-')
            strdict[k] = str(v)

        if sskey is None:
            sskey = self.get_sskey()
        #
        # keystr = self.get_tabbed_list_str(strdict.keys())
        #  logging.info(sheet_name + " info: " + keystr)

        # valstr = self.get_tabbed_list_str(strdict.values())
        #
        # logging.info(sheet_name + " vals: " + valstr)
        #
        # for k, v in strdict.items():
        #     test = {k: v}
        #     logging.debug("Inserting " + k + "\t: " + v)
        #     self.get_worksheet(sheet_name, sskey=sskey).insert_row(test)

        try:
            self.get_worksheet(sheet_name,sskey=sskey).insert_row(strdict)
        except Exception as e:
            # logging.info('caught: ' + str(e.message))
            if ('Blank rows cannot be written; use delete instead.' not in
                    str(e.message)):
                raise e



    def append_data_sheet_row(self, rowdata, sskey=None):
        self.append_sheet("Data", rowdata, sskey)

    def append_stats_sheet_row(self, rowdata, sskey=None):
        self.append_sheet("Stats", rowdata, sskey)


    def get_game_dict(self, ws, cols):

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

            statsrow = row
            # We have the capability to prune the columns that make it into
            # the stats stable, but more data is more better
            if cols is not None:
                statsrow = {}
                for k,v in row.items():
                    if k == id or k in cols:
                        statsrow[k] = v

            if realmval not in realms:
                # initialize a list of one row as second element in tuple
                realms[realmval] = (statsrow['id'],[statsrow])
            else:
                # append to the rows store din the second element of the tuple
                realms[realmval][1].append(statsrow)

        # logging.debug("Game Dict:\n" + pformat(gamedict))
        return gamedict


    def append_stats_rows(self, game_rows, num_bins, sskey=None):

        row_bins = bin_list(game_rows, num_bins)
        # logging.debug("Coverted:\n" + pformat(game_rows)+"\n\nTo:\n"+
        #     pformat(row_bins))

        if len(row_bins) != num_bins:
            raise Exception("There should only be " + str(num_bins) +
                            " bins BUT THERE ARE " + str(len(row_bins)))

        rows_written = 0

        for cur_bin_index in xrange(len(row_bins)):
            cur_bin = row_bins[cur_bin_index]
            outrow = {}
            outrow['bin-index'] = cur_bin_index
            number_keys = {}

            for bin_row in cur_bin:
                for key, value in bin_row.items():

                    # I think google inserts this attribute automatically
                    if "rowid" in key:
                        continue

                    if is_float(value) or is_int(value):
                        if key not in number_keys:
                            number_keys[key] = 1
                        else:
                            number_keys[key] += 1

                        if is_int(value):
                            value = int(value)
                        else:
                            value = float(value)

                        if value is not None and key not in outrow:
                            outrow[key] = value
                        else:
                            outrow[key] += value
                    elif value is not None:
                    #else:
                        outrow[key] = value


            # perform averaging of all stats in bins for each row for total history
            for number_key, n in number_keys.items():
                try:
                    outrow[number_key] /= n
                except:
                    raise Exception("Mixed data in " + str(number_key))

            # Now update the "last n" rows for the immediate history

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
            for key, value in hist_row.items():
                if "rowid" in key:
                    continue
                elif value is None:
                    continue

                newkey = key + "-last"
                # assign the value in the output row for the new key
                outrow[newkey] = value

            outrow['index'] = rows_written
            # logging.info("Sending row: " + str(outrow))
            self.append_stats_sheet_row(outrow, sskey=sskey)
            rows_written += 1

        if rows_written != num_bins:
            raise Exception("There are supposed to be " + str(num_bins) +
                            " but " + str(rows_written) + " were written")

    processing_stats = False

    def process_stats(self, cols=None, sskey=None):
        if WebData.processing_stats:
            logging.info("Stats are already being processed")
            return False

        try:
            logging.info("Stats being processed for data fields: " + str(cols))
            WebData.processing_stats = True

            dws = self.get_worksheet("Data", sskey=sskey)
            gamedict = self.get_game_dict(dws, cols)

            #logging.info("Got stats game dictionsry: \n" + pformat(gamedict))

            ws = self.get_worksheet("Stats", sskey=sskey)
            logging.info("Deleting rows, this takes a while...")
            ws.delete_all_rows()
            logging.info("After deleting there are " +
                          str(len(ws.get_rows())) + " rows")

            bins = 5

            for bbs_address, gamerec in gamedict.items():
                # this line is mainly to seperate sections
                #ws.insert_row({'bbs-address': str(bbs_address)})
                for game, realmrec in gamerec.items():
                    # this line is mainly to seperate sections
                    #ws.insert_row({'game-number': str(game)})
                    for realm,tup in realmrec.items():
                        # this line is mainly to seperate sections
                        #ws.insert_row({'realm-name': str(realm)})
                        gid =tup[0]
                        rows = tup[1]

                        logging.debug("Retrieved " + str(len(rows)) +
                                      " data rows for " + gid)

                        self.append_stats_rows(rows, bins, sskey=sskey)

            logging.debug("After processing stats there are" +
                          str(len(ws.get_rows())) + " rows")

        finally:
            logging.info("Stats are done being processed")
            WebData.processing_stats = False

