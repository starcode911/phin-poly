#!/usr/bin/env python3
"""
Polyglot v2 node server pHin Smart Water Monitor (c) 2020 starcode911
"""
import sys
import time
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
from nodes import Controller

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('pHin')
        polyglot.start()
        control = Controller.Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

