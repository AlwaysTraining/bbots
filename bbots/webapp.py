import time
from bbots.webdata import WebData
from bbots.webui import WebUi
from bbots.session import Session
import random
import logging
from datetime import datetime
from datetime import timedelta

# 60 minutes
SCHEDULER_PERIOD = 60*60
SCHEDULER_PERIOD = 1
# it will always be 24 hours for the game period, but you can adjust for
# testing
GAME_PERIOD = 24 * 60 * 60

def get_midnight():
    now = datetime.now()
    start = datetime(now.year, now.month, now.day,0,0,1)
    return start

class WebApp(object):
    def __init__(self,bbotslogfile, weblogfile):
        self.scheduler_period = SCHEDULER_PERIOD
        self.data = WebData(self)
        self.webui = WebUi()
        self.webui.bbotslogfile = bbotslogfile
        self.webui.weblogfile = weblogfile
        self.in_task = False

    def append_stats(self, stats, app):
        for k,v in app.options:
            if k in stats:
                raise Exception("Key collision in stats collection")
            stats[k] = v


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

        self.data.update_rec(rec)
        ui_row_num = self.webui.on_game_in_progress(rec)
        s = None

        try:
            s = Session(rec)

            if s.success == True:
                rec['successes'] += 1
                rec['status'] = "success"
                rec['last_completed_all_turns'] = datetime.now()

            else:
                rec['failures'] += 1
                rec['status'] = "failure"
        except Exception as e:
            logging.error("An exception escaped from the session object")
            logging.exception(e)
        finally:

            # blindly dump all parsed game data to dictionary
            stats = s.app.data.get_realm_dict()
            # clean stats taple for tample
            self.clean_stats(stats, s.app)
            key = self.data.get_ss_key()
            self.data.append_stats(stats,sskey=key)
            self.data.process_stats(sskey=key)

            logging.info("Updating persistant information")
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

            required_time_since_last_play = timedelta(minutes=random.randint(45,75))

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



    def scheduler_task(self):
        """
        Randomly try to play until we get into at least one bre game
        """
        try:
            if self.in_task == True:
                raise Exception("Currently in task!")
            self.in_task = False

            sleeptime = random.randint(0,SCHEDULER_PERIOD/3)
            logging.info("Randomly sleeping for " + str(round(sleeptime/60.0,1)) + " minutes")
            time.sleep(sleeptime)
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
            self.in_task = False



