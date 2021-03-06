import time
import os, subprocess
from bbots.webdata import WebData
from bbots.webui import WebUi
from bbots.session import Session
import random
import logging
from datetime import datetime
from datetime import timedelta

# 5 minutes
SCHEDULER_PERIOD = 5 * 60

# it will always be 24 hours for the game period, but you can adjust for
# testing
GAME_PERIOD = 24 * 60 * 60

def get_midnight():
    now = datetime.now()
    start = datetime(now.year, now.month, now.day,0,0,1)
    return start

class WebApp(object):
    def __init__(self,bbotslogfile, weblogfile, data_dir='.'):
        self.scheduler_period = SCHEDULER_PERIOD
        self.data = WebData(self)
        self.webui = WebUi(self)
        self.webui.bbotslogfile = bbotslogfile
        self.webui.weblogfile = weblogfile
        self.in_task = False
        self.stats_cols = None
        self.data_dir = data_dir
        # Because I can, I regenerate stats for all columns, but if you want
        # to do them all, set the cols to None
        # self.stats_cols = ['id', 'realm',
        #     'regions-number','score', 'networth']

    def clean_stats(self, stats, app):
        for k,v in app.options.items():
            if k in stats:
                raise Exception("Key collision in stats collection")
            stats[k] = v
        newstats = {}
        for k,v in stats.items():
            if 'password' in k:
                continue
            if 'menu_option' in k:
                continue
            if 'smtp' in k:
                continue
            if 'num_per_carrier' in k:
                continue
            if k == 'bank_investments':
                v = sum(v)

            newstats[k] = v

        return newstats


    def process_stats_data(self, s, recalc=True):
        # blindly dump all parsed game data to dictionary
        stats = s.app.data.get_realm_dict(allow_null=False)
        # clean stats table for sample
        stats = self.clean_stats(stats, s.app)
        key = self.data.get_sskey()
        self.data.append_data_sheet_row(stats, sskey=key)
        if recalc:
            self.data.process_stats(sskey=key, cols=self.stats_cols)

    def play_game(self, rec):
        """
        Play the game specified in the record
        """
        # Session(rec)
        logging.debug("Playing game: " + rec['id'])
        time.sleep(5)

        now = datetime.now()
        rec['last_attempt'] = now
        rec['status'] = "in progress"
        rec['data_dir'] = self.data_dir

        self.data.update_rec(rec)
        ui_row_num = self.webui.on_game_in_progress(rec)
        s = None
        logdata = rec['force_record_data']

        try:
            s = Session(rec)

            if s.success == True:
                rec['successes'] += 1
                rec['status'] = "success"
                if s.app.metadata.used_all_turns:
                    rec['last_completed_all_turns'] = datetime.now()
                    logdata = True
            else:
                rec['failures'] += 1
                rec['status'] = "failure"
        except Exception as e:
            logging.error("An exception escaped from the session object")
            logging.exception(e)
        finally:

            try:
                if not logdata and s.app.metadata.used_all_turns:
                    logdata = True

                if logdata:
                    logging.info("Updating data statistics")
                    self.process_stats_data(s,recalc=False)
            except Exception as e2:
                logging.error("An exception occurred while processing stats")
                logging.exception(e2)

            logging.info("Updating persistant game information")
            self.data.update_rec(rec)
            self.webui.on_update_ui_row(ui_row_num, rec)
            logging.info("Done playing game")
        return True



    def maybe_play_game(self, id):
        """
        Check if conditions are correct to play game and play it
        """
        rec = self.data.get_record(id)
        id = str(rec['id'])
        logging.debug("considering playing game: " + id)

        if not rec['enabled']:
            logging.debug(id +" is disabled")
            return False

        midnight = get_midnight()

        first_play = midnight + timedelta(hours=rec[
            'hour_delay_from_midnight_to_first_play'])

        logging.debug("The earliest time of the day I would consider playing is: " + str(first_play))

        now = datetime.now()

        too_early = now < first_play
        if too_early:
            logging.debug("It is too early in the day to play, we must wait until " + 
                    str(first_play))
            return False

        if 'last_attempt' in rec:
            last_attempt = rec['last_attempt']
        else:
            last_attempt = None


        if last_attempt is not None:
            time_since_last_play = now - last_attempt

            required_time_since_last_play = timedelta(
                hours=rec['hour_delay_redial'])

            if time_since_last_play < required_time_since_last_play:
                logging.debug("we just played: " + str(time_since_last_play) +
                        " ago, but it is required we wait at least " + 
                        str(required_time_since_last_play))
                return False

        if 'last_completed_all_turns' in rec:
            last_completed_all_turns = rec['last_completed_all_turns']
        else:
            last_completed_all_turns = None

#        next_play = first_play + timedelta(minutes=GAME_PERIOD)

        if last_completed_all_turns is not None:
            already_played = last_completed_all_turns > first_play
            if already_played:
                logging.debug("We already used all of our turns today at: " + 
                    str(last_completed_all_turns))
                return False


        logging.debug('I could not find a single temporal reason not to '
                      'play: ' + id)

        return self.play_game(rec)


    def git_pull(self):
        try:
            appdir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cmd = "cd " + appdir + " && ./pull.sh"
            logging.debug("Running: " + cmd)

            output = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      shell=True).communicate(

            )[0]

            return output

        except Exception, e:
            logging.exception(e)
            logging.warn("Could not git changes")

        return "Could not get recent source code changes"

    def scheduler_task(self):
        """
        Randomly try to play until we get into at least one bre game
        """
        try:
            if self.in_task == True:
                raise Exception("Currently in task!")
            self.in_task = True

            sleeptime = random.randint(0,SCHEDULER_PERIOD/3)
            logging.info("Randomly sleeping for " + str(round(sleeptime/60.0,1)) + " minutes")
            time.sleep(sleeptime)

            self.git_pull()

            self.data.load_ss()
            ids = list(self.data.ids)
            random.shuffle(ids)
            for id in ids:
                if self.maybe_play_game(id):
                    return
        except Exception as ex:
            logging.error("Exception was thrown out to tasking function")
            logging.exception(ex)
        finally:
            self.git_pull()
            self.in_task = False




