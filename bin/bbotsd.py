#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os

import logging
import time
import cherrypy
from bbots.webapp import WebApp




def main():


    logging.basicConfig(
        # filename='bbots.log',
        level=logging.DEBUG)

    app = WebApp()
    wd = cherrypy.process.plugins.BackgroundTask(app.scheduler_period,
                                                 app.scheduler_task)
    wd.start()
    cherrypy.quickstart(app.webui,config=os.path.join(
        os.path.dirname(__file__), 'bbots.conf'))


if __name__ == '__main__':
    main()



