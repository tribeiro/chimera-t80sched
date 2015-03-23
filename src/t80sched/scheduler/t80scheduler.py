
from chimera.controllers.scheduler import controller

from chimera.controllers.scheduler.machine import Machine
from chimera.controllers.scheduler.executor import ProgramExecutor

from chimera.core.exceptions import ObjectNotFoundException, ChimeraException

from t80sched.scheduler import queue

class T80Scheduler(controller.Scheduler):

    #__config__ = {"seeingmonitor" : "/SeeingMonitor/0"}

    def __init__(self):
        controller.Scheduler.__init__(self)
    

    def __start__(self):

        self.executor = ProgramExecutor(self)
        self.scheduler = queue.QueueScheduler()
        self.machine = Machine(self.scheduler, self.executor, self)
        self.scheduler.site = self.getManager().getProxy("/Site/0")

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