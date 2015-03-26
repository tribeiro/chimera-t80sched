
'''
    A queue executer for chimera. This is just like a sequential executor with
    the difference that it will 
'''

#from chimera.controllers.scheduler.ischeduler import IScheduler
#from chimera.controllers.scheduler.model import Session, Program
from chimera.util.position import Position

from chimera.core.site import (Site, datetimeFromJD)

from t80sched.scheduler.model import Session, Program, Targets, BlockPar

#from sqlalchemy import (desc, asc)

#import chimera.core.log
import logging #as log

log = logging.getLogger("chimera.controllers.scheduler.t80sched")

import numpy as np

class fakeSM():
    def seeing(self,time=None):
        return -1

class QueueScheduler ():

    def __init__ (self,site):
        self.site = site
        self.seeingmonitor = fakeSM()

    def next (self, nowmjd=None):

        #session = Session()

        if not nowmjd:
            nowmjd=self.site.MJD()

        program = None

        # Get a list of priorities
        plist = self.getPList()

        if len(plist) == 0:
            return None

        # Get project with highest priority as reference
        priority = plist[0]
        program,plen = self.getProgram(nowmjd,plist[0])

        if program and ( (not program.slewAt) and (self.checkConditions(program,nowmjd))):
            # Program should be done right away!
            return program

        for p in plist[1:]:

            # Get program and program duration (lenght)
            aprogram,aplen = self.getProgram(nowmjd,p)

            if not aprogram:
                continue

            if not program:
                program = aprogram

            if not self.checkConditions(aprogram,program.slewAt):
                # if condition is False, project cannot be executed. Go to next in the list
                continue

            #return program
            #if aplen < 0 and program:
            #	log.debug('Using normal program (aplen < 0)...')
            #	return program

            # If alternate program fits will send it instead
            waittime=(program.slewAt-nowmjd)*86.4e3
            if waittime>aplen:
                log.debug('Choose program with priority %i'%p)
                # put program back with same priority
                #self.rq.put((prt,program))
                # return alternate program
                return aprogram
            if not self.checkConditions(program,program.slewAt):
                program,plen = aprogram,aplen
            #program,plen,priority = aprogram,aplen,p
            #if not program.slewAt :
            #    # Program should be done right now if possible!
            #    # TEST "if possible"
            #    log.debug('Choose program with priority %i'%p)
            #    return program


        if not self.checkConditions(program,program.slewAt):
            # if project cannot be executed return nothing.
            # [TO-CHECK] What the scheduler will do? should sleep for a while and
            # [TO-CHECK] try again.
            return None

        log.debug('Choose program with priority %i'%priority)
        return program
        '''
        else:
            site = Site()
            nowmjd=site.MJD()
            altprogram,aplen = self.getAlternateProgram(nowmjd)
            return altprogram
        '''

        return None

    def done (self, task, error=None):

        if error:
            log.debug("Error processing program %s." % str(task))
            log.exception(error)
        else:
            task.finished = True

        #self.rq.task_done()
        self.machine.wakeup()


    def getProgram(self,nowmjd,priority):

        session = Session()

        program1 = session.query(Program).filter(Program.finished == False).filter(Program.priority == priority).filter(Program.slewAt > nowmjd).order_by(Program.slewAt).first()

        program2 = session.query(Program).filter(Program.finished == False).filter(Program.priority == priority).filter(Program.slewAt < nowmjd).order_by(Program.slewAt.desc()).first()

        if not program1 and not program2:
            log.debug('No program in alternate queue %i'%priority)
            session.commit()
            return None,-1

        elif not program1:
            log.debug('No program1 in alternate queue %i'%priority)
            dT = 0
            for ii,act in enumerate(program2.actions):
                if ii > 0:
                    dT+=act.exptime*act.frames
            session.commit()
            return program2,dT

        elif not program2:
            log.debug('No program2 in alternate queue %i'%priority)
            dT = 0
            for ii,act in enumerate(program1.actions):
                if ii > 0:
                    dT+=act.exptime*act.frames
            session.commit()
            return program1,dT

        log.debug('Found 2 suitable programs in alternate queue %i'%priority)

        # Still need to check sky condition (seeing, moon, sky transparency....), altitude, moon...

        wtime1 = (program1.slewAt-nowmjd)
        wtime2 = (nowmjd-program2.slewAt)

        if wtime1 < wtime2:
            log.debug('Program1 closer')
            dT = 0
            for ii,act in enumerate(program1.actions):
                if ii > 0:
                    dT+=act.exptime*act.frames
            session.commit()
            return program1,dT
        else:
            log.debug('Program2 closer')
            dT = 0
            for ii,act in enumerate(program2.actions):
                if ii > 0:
                    dT+=act.exptime*act.frames
            session.commit()
            return program2,dT

        session.commit()
        return None,-1

    def getPList(self):

        session = Session()
        plist = [p[0] for p in session.query(Program.priority).distinct().order_by(Program.priority)]
        session.commit()

        return plist

    def checkConditions(self, prg, time):
        '''
        Check if a program can be executed given all restrictions imposed by airmass, moon distance,
         seeing, cloud cover, etc...

        [comment] There must be a good way of letting the user rewrite this easily. I can only
         think about a decorator but I am not sure how to implement it.

        :param program:
        :return: True (Program can be executed) | False (Program cannot be executed)
        '''

        # 1) check airmass
        session = Session()
        program = session.merge(prg)
        target = session.query(Targets).filter(Targets.id == program.tid).first()
        blockpar = session.query(BlockPar).filter(BlockPar.pid == program.pid).filter(BlockPar.bid == program.blockid).first()

        raDec = Position.fromRaDec(target.targetRa,target.targetDec)
        #print program,target
        dateTime = datetimeFromJD(time+2400000.5)
        lst = self.site.LST_inRads(dateTime) # in radians

        alt = float(self.site.raDecToAltAz(raDec,lst).alt)
        airmass = 1./np.cos(np.pi/2.-alt*np.pi/180.)

        if blockpar.minairmass < airmass < blockpar.maxairmass:
            log.debug('\tairmass:%.3f'%airmass)
            pass
        else:
            log.warning('Target out of range airmass... (%f < %f < %f)'%(blockpar.minairmass, airmass, blockpar.maxairmass))
            return False

        # 2) check moon Brightness

        moonBrightness = self.site.moonphase(dateTime)*100.
        if blockpar.minmoonBright < moonBrightness < blockpar.maxmoonBright:
            log.debug('\tmoonBrightness:%.2f'%moonBrightness)
            pass
        else:
            log.warning('Wrong Moon Brightness... (%f < %f < %f)'%(blockpar.minmoonBright,
                                                                   moonBrightness,
                                                                   blockpar.maxmoonBright))
            return False

        # 3) check moon distance
        moonRaDec = self.site.altAzToRaDec(self.site.moonpos(dateTime),lst)

        moonDist = raDec.angsep(moonRaDec)

        if moonDist < blockpar.minmoonDist:
            log.warning('Object to close to the moon... (moonDist = %f | minmoonDist = %f)'%(moonDist,
                                                                                             blockpar.minmoonDist))
            return False
        else:
            log.debug('\tMoon distance:%.3f'%moonDist)
        # 4) check seeing

        seeing = self.seeingmonitor.seeing(time)

        if seeing > blockpar.maxseeing:
            log.warning('Seeing higher than specified... sm = %f | max = %f'%(seeing,
                                                                              blockpar.maxseeing))
            return False
        elif seeing < 0.:
            log.warning('No seeing measurement...')
        else:
            log.debug('Seeing %.3f'%seeing)
        # 5) check cloud cover

        log.debug('Target OK!')
        return True
