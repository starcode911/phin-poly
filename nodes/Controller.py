#!/usr/bin/env python3
"""
Polyglot v2 node server pHin Smart Water Monitor data

This version only support a single pHin monitor

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
import uuid;
import ns_parameters
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'phin'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)


        LOGGER.info('init')
      

        self.name = 'pHin Smart Water Monitor'
        self.address = 'phin'
        self.primary = self.address
        self.configured = False
        self.uom = {}
        self.logger = polyinterface.LOGGER

        #
        # Generate a UUID that will indentify this "device" 
        #
        self.uuid = str(uuid.uuid4())


        self.params = ns_parameters.NSParameters([
            {
            'name': 'email',
            'default': 'email',
            'isRequired': True,
            'notice': 'Enter the email your used to sign up for the pHin service',
            },
             {
            'name': 'Verification Code',
            'default': 'set me',
            'isRequired': True,
            'notice': 'After you entered your email enter the Verification Code you received by email',
            },
            {
            'name': 'Token',
            'default': '<do not enter>',
            'isRequired': True,
            'notice': '',
            },
           {
            'name': 'uuid',
            'default': self.uuid,
            'isRequired': True,
            'notice': '',
            },
             {
            'name': 'vesselurl',
            'default': '<do not enter>',
            'isRequired': True,
            'notice': '',
            },

            ])

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):

        LOGGER.info('process_config')
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

    
    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
        self.discover()

        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_conditions(True)

    def longPoll(self):
        LOGGER.info('longPoll')
        return

    def shortPoll(self):
        LOGGER.info('shortPoll')
        self.query_conditions(False)

    def get_phin_data(self, url_param, extra=None):
        LOGGER.info('get_phin_data')
        return None

    """
        Query the pHin service for the pool data
    """
    def query_conditions(self, force):

        LOGGER.info('query_conditions')
        #if not self.configured:
        #    LOGGER.info('Skipping connection because we aren\'t configured yet.')
        #    return

        jdata = self.get_phin_data('current')

        # Should we check that jdata actually has something in it?
        #if jdata == None:
        #   LOGGER.error('Current condition query returned no data')
        #  return

       
        self.setDriver('WATERT', '101', force)
        self.setDriver('GV1', '7.1', force)
        



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

        LOGGER.info('check_params')
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

        # angelo
        level=10

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

