import time
from bbots.webdata import WebData
from bbots.webui import WebUi
import random
import logging
from datetime import datetime
from datetime import timedelta

SCHEDULER_PERIOD = 5
# it will always be 24 hours for the game period, but you can adjust for
# testing
GAME_PERIOD = 24 * 60 * 60

def get_midnight():
    now = datetime.now()
    start = datetime(now.year, now.month, now.day,0,0,1)
    return start

class WebApp(object):
    def __init__(self):
        self.scheduler_period = SCHEDULER_PERIOD
        self.data = WebData(self)
        self.webui = WebUi()

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
        s = Session(rec)


        if s.success == True:
            rec['last_success'] = now
            rec['successes'] += 1
            rec['status'] = "success"
        else:
            rec['failures'] += 1
            rec['status'] = "failure"




        self.data.update_rec(rec)
        self.webui.on_update_ui_row(ui_row_num, rec)
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

        now = datetime.now()

        too_early = now < first_play
        if too_early:
            logging.debug("It is too early in the day to play: " + id)
            return False


        if 'last_attempt' in rec:
            last_attempt = rec['last_attempt']
        else:
            last_attempt = None


        if last_attempt is not None:
            just_tried = now > (
                last_attempt + timedelta(minutes=random.randint(45,75)))
            if just_tried:
                logging.debug("we just tried to play: " + id)
                return False

        if 'last_completed_all_turns' in rec:
            last_completed_all_turns = rec['last_completed_all_turns']
        else:
            last_completed_all_turns = None

        next_play = first_play + timedelta(minutes=GAME_PERIOD)

        if last_completed_all_turns is not None:
            already_played = last_completed_all_turns < next_play
            if already_played:
                logging.debug("We already used all of our turns today")
                return False


        logging.debug('I could not find a single temporal reason not to '
                      'play: ' + id)

        return self.play_game(rec)



    def scheduler_task(self):
        """
        Randomly try to play until we get into at least one bre game
        """
        self.data.load_ss()
        ids = list(self.data.ids)
        random.shuffle(ids)
        for id in ids:
            if self.maybe_play_game(id):
                return



