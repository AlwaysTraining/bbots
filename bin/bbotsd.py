#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os

import logging
import time
import cherrypy
from bbots.webapp import WebApp




def main():

    logging.basicConfig(
        format='%(asctime)s:%(levelname)s::%(message)s',
        level=logging.DEBUG,
        filename='bbotsd.log')

    botlogfile = os.path.join(
            os.getcwd(),'bbotsd.log')

    # this is a hack, hardcode weblog file, which is set in the startup script
    # start.sh
    weblogfile = os.path.join(
            os.getcwd(),'webapp.log')

    app = WebApp(botlogfile, weblogfile, data_dir='.')

    wd = cherrypy.process.plugins.BackgroundTask(app.scheduler_period,
                                                 app.scheduler_task)
    wd.start()
    cherrypy.quickstart(app.webui,config=os.path.join(
        os.path.dirname(__file__), 'bbots.conf'))


if __name__ == '__main__':
    main()



