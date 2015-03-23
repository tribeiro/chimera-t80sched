__author__ = 'tiago'

from chimera.core.site import (Site, datetimeFromJD)

from chimera.core.chimeraobject import ChimeraObject

class Checker(ChimeraObject):
    def __init__(self):
        ChimeraObject.__init__(self)
        self.site = None

    def __start__(self):
        self.site = self.getManager().getProxy("/Site/0")

def checkConditions(program, time):
    '''
    Check if a program can be executed given all restrictions imposed by airmass, moon distance,
     seeing, cloud cover, etc...

    [comment] There must be a good way of letting the user rewrite this easily. I can only
     think about a decorator but I am not sure how to implement it.

    :param program:
    :return: True (Program can be executed) | False (Program cannot be executed)
    '''

    checker = Checker()
    print checker.site['name']
    # 1) check airmass

    # 2) check moon Brightness

    # 3) check moon distance

    # 4) check seeing

    # 5) check cloud cover

    return True
