
from chimera.controllers.scheduler import controller

from chimera.controllers.scheduler.machine import Machine
from chimera.controllers.scheduler.executor import ProgramExecutor

from chimera.core.exceptions import ObjectNotFoundException, ChimeraException

from t80sched.scheduler import queue
from t80sched.scheduler.model import AutoGuide
from t80sched.scheduler.handlers import AutoGuiderHandler

class T80Scheduler(controller.Scheduler):

    __config__ = {"autoguider" : "/AutoGuider/0"}

    def __init__(self):
        controller.Scheduler.__init__(self)
    

    def __start__(self):

        self.executor = ProgramExecutor(self)
        t80handlers = {AutoGuide: AutoGuiderHandler}

        self.executor.actionHandlers.update(t80handlers)

        for handler in t80handlers.values():
            self.executor._injectInstrument(handler)

        self.scheduler = queue.QueueScheduler(self.getManager().getProxy(self["site"]))
        self.machine = Machine(self.scheduler, self.executor, self)

        try:
            self.scheduler.seeingmonitor = self.getManager().getProxy("/SeeingMonitor/0")
        except ObjectNotFoundException:
            class fakeSM():
                def seeing(self,time=None):
                    return -1
            #self.seeingmonitor = fakeSM()

            self.scheduler.seeingmonitor = fakeSM()
        except:
            raise

        self.log.debug("Using %s algorithm" % self["algorithm"])

    def next(self,nowmjd):
        return self.scheduler.next(nowmjd)