from bbot.App import App
import logging


def query(key):
    if key == 'data_dir':
        return '.'
    raise Exception("Need value provided for: %s" % key)


def query_secret(prompt):
    raise Exception("Need secret value provided for: %s" % prompt)


class Session:

    def __init__(self, rec):
        self.success = False
        self.rec = rec

        try:
            self.app = App(rec, query, query_secret)
            self.app.run()
            self.success = True
        except Exception, e:
            self.exception = e
            logging.error("Failed when playing: " + self.rec['id'])
            logging.exception(e)




