
from chimera.core.exceptions import ProgramExecutionException,printException
from chimera.controllers.scheduler.handlers import (requires,ActionHandler)

import copy

class AutoGuiderHandler(ActionHandler):

    @staticmethod
    @requires("autoguider")
    def process(action):

        if action.stop:
            AutoGuiderHandler.abort(action)
        else:
            guiding = False
            ag = AutoGuiderHandler.autoguider

            for iter in range(action.ntries):
                try:
                    ag.guide(exptime=action.min_exptime+iter*action.max_exptime/action.ntries,
                             filter=action.filter,
                             binning=action.binning,
                             windowCCD=action.windowCCD,
                             box=action.box)
                except Exception, e:
                    pass
                else:
                    guiding = True
                    break

        if not guiding:
            raise ProgramExecutionException("Could not start guider.")

    @staticmethod
    def abort(action):
        ag = copy.copy(AutoGuiderHandler.autoguider)
        ag.stop()

    @staticmethod
    def log(action):
        if action.stop:
            return "autoguider: stop"
        else:
            return "autoguider: start"

