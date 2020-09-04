#!/usr/bin/env python3
"""
Polyglot v2 node server pHin Smart Water Monitor data
Copyright (C) 2020 starcode911
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import datetime
import requests
import socket
import math
import re
import json
import ns_parameters
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'phin'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'pHin Smart Water Monitor'
        self.address = 'phin'
        self.primary = self.address
        self.configured = False
        self.uom = {}

        self.params = ns_parameters.NSParameters([{
            'name': 'Token',
            'default': 'set me',
            'isRequired': True,
            'notice': 'pHin oAuth Token needs to be set',
            },
             {
            'name': 'email',
            'default': 'email',
            'isRequired': True,
            'notice': 'Email you used to sign up for pHin',
            },
             {
            'name': 'Verification Code',
            'default': 'set me',
            'isRequired': True,
            'notice': 'Verification Code received by email ',
            },
            ])

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            LOGGER.debug('-- configuration not yet valid')
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            LOGGER.debug('-- configuration is valid')
            self.removeNoticesAll()
            self.configured = True
            self.discover()
        elif valid:
            LOGGER.debug('-- configuration not changed, but is valid')
            # is this necessary
            #self.configured = True

    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
        self.discover()

        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_conditions(True)

    def longPoll(self):
        return

    def shortPoll(self):
        self.query_conditions(False)

    def get_phin_data(self, url_param, extra=None):
        return NONE

    """
        Query the pHin service for the pool data
    """
    def query_conditions(self, force):


        #if not self.configured:
        #    LOGGER.info('Skipping connection because we aren\'t configured yet.')
        #    return

        #jdata = self.get_phin_data('current')

        # Should we check that jdata actually has something in it?
        #if jdata == None:
        #   LOGGER.error('Current condition query returned no data')
        #  return

       
        self.update_driver('WATERT', 101, force)
        self.update_driver('GV1', 7.1, force)
        



    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
       LOGGER.info('Discover node server')

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):

        # NEW code, try this:
        self.removeNoticesAll()

        if self.params.get_from_polyglot(self):
            LOGGER.debug('All required parameters are set!')
            self.configured = True
        else:
            LOGGER.debug('Configuration required.')
            LOGGER.debug('apikey = ' + self.params.get('Token'))
            self.params.send_notices(self)

    # Set the uom dictionary based on current user units preference
    def set_driver_uom(self, units):
        LOGGER.info('New Configure driver units to ' + units)

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                #level = self.getDriver('GV21')
                level = self.get_saved_log_level()
            except:
                LOGGER.error('set_logging_level: get GV21 value failed.')

            if level is None:
                level = 30
            level = int(level)
        else:
            level = int(level['value'])

        #self.setDriver('GV21', level, True, True)
        self.save_log_level(level)

        LOGGER.info('set_logging_level: Setting log level to %d' % level)
        LOGGER.setLevel(level)


    commands = {
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'DEBUG': set_logging_level,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'WATERT', 'value': 0, 'uom': 4},   # water temperature
            {'driver': 'GV1', 'value': 0, 'uom': 4},       # pH level
            {'driver': 'GV21', 'value': 0, 'uom': 25},     # log level
            ]

