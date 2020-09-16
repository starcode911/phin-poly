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


from pyPhin import pHin

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):

    id = 'phin'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)

        self.name       = 'pHin Smart Water Monitor'
        self.address    = 'phin'
        self.primary    = self.address

        self.activating  = False
        self.activated   = False
        self.registering = False
        self.registered  = False
        self.configuring = False

        self.test        = False


        self.uom        = {}
        self.logger     = polyinterface.LOGGER
        self.phin       = pHin(LOGGER)

        self.poly.onConfig(self.processConfig)

       

    #
    # Generate a UUID that will indentify this "device" 
    #
    def getGeneratedUUID(self):
        deviceuuid = str(uuid.uuid4())
        LOGGER.debug("uuid=%s", deviceuuid)
        return deviceuuid;


    def getEmail(self):
            email = self.getCustomParam('email')

            if not email:
                return None
            
            # 
            # check if we are having a valid email address
            #
            regex = "[^@]+@[^@]+\.[^@]+"
            if(not re.search(regex,email)):  
                return None

            return email



    def getUUID(self):
            uuid = self.getCustomParam('uuid')
            if not uuid:
                return None
            if len(uuid) < 20:
                return None
            return uuid

    def getVerifyURL(self):
            verifyurl = self.getCustomParam('verifyurl')
            if not verifyurl:
                return None
            if len(verifyurl) < 20:
                return None
            return verifyurl

    def getActivationCode(self):
            activationcode = self.getCustomParam('activationcode')
            if not activationcode:
                return None
            if len(activationcode) > 10:
                return None
            if not activationcode.isnumeric():
                return None
            return activationcode


    def getAuthToken(self):
        authtoken = self.getCustomParam('authtoken')
        if not authtoken:
            return None
        if len(authtoken) < 40:
            return None
        return authtoken
  
    def getVesselURL(self):
        vesselurl = self.getCustomParam('vesselurl')
        if not vesselurl:
            return None
        if len(vesselurl) < 20:
            return None
        return vesselurl


    #
    #
    #
    def addActivationCodeParam(self):
        LOGGER.debug('status=ADD_ACTIVATIONCODE_PARAM')
        self.addCustomParam({'activationcode' : '<Enter activation code>'})


    # 
    # Clear the configuration due to the auth token no longer being
    # valid. We can leave the UUID and email address
    # 
    def resetConfig(self):
        LOGGER.debug('status=RESET_CONFIG')

        self.configuring = True

        self.addNotice('Please check your email and enter the 5-digit activation code', 'activationcode')

        self.removeCustomParam('authtoken')
        self.removeCustomParam('vesselurl')
        self.removeCustomParam('activationcode')

        self.addActivationCodeParam()

        self.registering = False
        self.registered = False
        self.activating = False
        self.activated = False

        self.configuring = False
    

    #
    # Restart our node server
    #
    def restartNodeServer(self):
        LOGGER.info('status=restart')
        self.restart()


    #
    # Process changes to customParameters
    #
    def processConfig(self, config):

        LOGGER.debug('status=START_processConfig')

        if self.configuring is True: 
            return

        #
        # if we have an auth token we are all set and
        # can query the service
        #
        if not self.getAuthToken():

            LOGGER.debug('status=CONFIG_INCOMPLETE registering=%r registered=%r activating=%r activated=%r',
                                self.registering,
                                self.registered,
                                self.activating,
                                self.activated
                        )


            if self.getCustomParam('email')  is None:
                
                LOGGER.debug('status=CONFIG_REQUEST_EMAIL')

                self.addCustomParam({'email' : 'Enter your email'})

                self.removeNoticesAll()
                self.addNotice('Enter the email you used to register with pHin', 'email')


            if self.getEmail() is not None:

                #
                # we have a valid email new lets set a UUID
                #
                if self.getUUID() is None:

                    LOGGER.debug("status=CONFIG_ADDING_UUID email=%s uuid=%s",
                                    self.getEmail(),   
                                    self.getUUID()
                                )

                    self.addCustomParam({'uuid' : self.getGeneratedUUID()})    


            #
            # we have an email but uuid has not been set yet, in this
            # scenario we want create a uuid and register the device
            # so we receive an activation token
            # If we already have a verifyURL we have registered already
            # and are waiting for the user to enter the validation code
            #
            if self.getEmail() and self.getUUID() and self.registering is False:
                if not self.getVerifyURL():

                    self.registering = True

                    #
                    # We have an email address so lets register this
                    # with the uuid (locally generated). This will cause
                    # the service to email a activation code that we will need
                    # for the next step
                    #
                    LOGGER.info("status=CONFIG_REGISTER email=%s uuid=%s", 
                                    self.getEmail(), 
                                    self.getUUID()
                                )

                    verifyurl = self.phin.login(self.getEmail(), self.getUUID())
                    self.addCustomParam({'verifyurl' : verifyurl})

                    self.removeNoticesAll()

                    self.addActivationCodeParam()

                    self.addNotice('Please check your email and enter the 5-digit activation code', 'activationcode')

                    self.registering = False
                    self.registered = True


                else:
                    if self.getActivationCode() is not None and self.activating is False and self.activated is False:

                        self.activating = True

                        LOGGER.debug("status=CONFIG_ACTIVATING email=%s uuid=%s verifyurl=%s activationcode=%s", 
                                                self.getEmail(), 
                                                self.getUUID(),
                                                self.getVerifyURL(),
                                                self.getActivationCode()
                                    )

                        try:
                            authdata = self.phin.verify(self.getEmail(), self.getUUID(), self.getVerifyURL(), self.getActivationCode())
                            self.addCustomParam({'authtoken' : authdata['authToken']})
                            self.addCustomParam({'vesselurl' : authdata['vesselUrl']})

                            #
                            # Setup configuraton has been completed. At this time we do no longer
                            # need the verifyURL and the Activation code
                            # TODO: Delete them?
                            #
                            LOGGER.debug("status=CONFIG_COMPLETED email=%s uuid=%s vesselurl=%s authtoken=%s", 
                                                self.getEmail(), 
                                                self.getUUID(),
                                                self.getVesselURL(),
                                                self.getAuthToken()
                                        )

                            self.removeNoticesAll()

                            #
                            #  get the data
                            #
                            self.queryPoolData()


                        except Exception as err:
                            e = str(err)
                            LOGGER.error('exception phin.getData error=%s', str(err))
                            if e.find('The code you provided is incorrect') != -1:
                                #
                                # we entered an invalid validation code - reset the code
                                #
                                self.addActivationCodeParam();
                                self.restartNodeServer()
            else:
                LOGGER.debug('status=passconfig authtoken=%s', self.getAuthToken())

        else:
            LOGGER.debug('status=noauthtoken authtoken=%s', self.getAuthToken())


        LOGGER.debug('status=END_processConfig')


    
    def start(self):
        LOGGER.info('Starting node server')
        self.setLogLevel()
        self.discover()

        LOGGER.info('Node server started')

        #
        # Do an initial query to get filled in as soon as possible
        #
        self.queryPoolData()

    def longPoll(self):
        LOGGER.info('longPoll')
        return

    def shortPoll(self):
        LOGGER.info('shortPoll')
        self.queryPoolData()


    #
    # If we have an auth token query the pHin service for the pool data
    #
    def queryPoolData(self):

        LOGGER.info('queryPoolData')

        if self.getAuthToken():
            try:
                data = self.phin.getData(self.getAuthToken(), self.getUUID(), self.getVesselURL())
            except Exception as err:
                e = str(err)
                LOGGER.error('exception phin.getData error=%s', str(err))
                if e.find('Unauthorized') != -1:
                    #
                    # Auth token is no longer valid, user will need to enter a new
                    # registration code from their email in order to obtain
                    # a new token
                    #
                    self.resetConfig()
                    self.restartNodeServer()

                data = None

            LOGGER.debug('phin.getData data='+str(data))
            if data:
                LOGGER.info("setDriver WATERT=%s", data['waterData']['temperature'])
                self.setDriver('WATERT', data['waterData']['temperature'], force=True)
                self.setDriver('GV2', int(data['pool']['status_id']), force=True)
                self.setDriver('GV3', data['waterData']['ta'], force=True)
                self.setDriver('GV4', data['waterData']['cya'], force=True)
                self.setDriver('GV5', data['waterData']['th'], force=True)
                self.setDriver('GV1', round(data['waterData']['ph']['value'], 1), force=True)
                self.setDriver('GV6', int(data['waterData']['ph']['status']), force=True)
                self.setDriver('GV7', data['waterData']['orp']['value'], force=True)
                self.setDriver('GV8', int(data['waterData']['orp']['status']), force=True)
                self.setDriver('GV9', (data['vesselData']['battery']['percentage']*100), force=True)
                self.setDriver('GV10', data['vesselData']['rssi']['value'], force=True)
        else:
                LOGGER.debug("status=noauthtoken")
            

    def query(self):
        LOGGER.info('query...')
        self.reportDrivers()

    def discover(self, *args, **kwargs):
       LOGGER.info('Discover node server')

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def updateProfile(self, command):
        st = self.poly.installprofile()
        return st


    #    
    #
    #
    def removeAllNotices(self, command):
        self.removeNoticesAll()

    #
    #
    #
    def setLogLevel(self, level=None):
        LOGGER.debug("loglevel=%s", str(level))

        # angelo
        level=10

        #self.save_log_level(level)

        LOGGER.info('setLogLevel: Setting log level to %d' % level)
        LOGGER.setLevel(level)




    commands = {
        'UPDATE_PROFILE': updateProfile,
        'REMOVE_NOTICES_ALL': removeAllNotices,
        'DEBUG': setLogLevel,
    }

    #
    # For this node server, all of the info is available in the single
    # controller node.
    #
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'WATERT', 'value': 0, 'uom': 4},   # water temperature
            {'driver': 'GV1', 'value': 0, 'uom': 56},       # pH level
            {'driver': 'GV2', 'value': 0, 'uom': 25},       # status
            {'driver': 'GV3', 'value': 0, 'uom': 54},       # TA
            {'driver': 'GV4', 'value': 0, 'uom': 54},       # CYA
            {'driver': 'GV5', 'value': 0, 'uom': 54},       # TH
            {'driver': 'GV6', 'value': 0, 'uom': 25},       # pH Status 
            {'driver': 'GV7', 'value': 0, 'uom': 43},       # ORP
            {'driver': 'GV8', 'value': 0, 'uom': 25},       # ORP Status
            {'driver': 'GV9', 'value': 0, 'uom': 51},       # Battery
            {'driver': 'GV10', 'value': 0, 'uom': 12},       # RSSI
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # log level
    ]




