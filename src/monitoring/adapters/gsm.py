'''
Created on 2018. jan. 7.

@author: gkovacs
'''
import json
import logging
import os

from gsmmodem.modem import GsmModem
from gsmmodem.exceptions import PinRequiredError, IncorrectPinError, TimeoutException
from monitoring.constants import LOG_ADGSM
from models import Option


class GSM(object):

    def __init__(self):
        self._logger = logging.getLogger(LOG_ADGSM)

    def setup(self):
        section = Option.query.filter_by(name='notifications', section='gsm').first()
        self._options = json.loads(section.value) if section else {'pin_code':''}
        self._options['port'] = os.environ['GSM_PORT']
        self._options['baud'] = os.environ['GSM_PORT_BAUD']

        self._modem = GsmModem(self._options['port'], self._options['baud'])
        self._modem.smsTextMode = True

        self._logger.info('Connecting to GSM modem on %s with %s baud (PIN: %s)...', 
                          self._options['port'],
                          self._options['baud'],
                          self._options['pin_code'])
        try:
            self._modem.connect(self._options['pin_code'], waitingForModemToStartInSeconds=10)
            self._logger.debug("GSM modem connected")
        except PinRequiredError:
            self._logger.error('Error: SIM card PIN required. Please specify a PIN with the -p argument')
            self._modem = None
            return False
        except IncorrectPinError:
            self._logger.error('Error: Incorrect SIM card PIN entered')
            self._modem = None
            return False
        except TimeoutException as error:
            self._logger.error('Error: no answer from GSM module: %s', error)
            self._modem = None
            return False

    def destroy(self):
        self._modem.close()

    def sendSMS(self, phone_number, message):
        if not self._modem:
            self.setup()
            
        if not self._modem:
            return False
        
        if message is None:
            return False

        self._logger.debug('Checking for network coverage...')
        try:
            self._modem.waitForNetworkCoverage(5)
        except TimeoutException:
            self._logger.error('Network signal strength is not sufficient, please adjust modem position/antenna and try again.')
            return False
        else:
            try:
                sms = self._modem.sendSms(phone_number, message)
            except TimeoutException:
                self._logger.error('Failed to send message: the send operation timed out')
                return False
            else:
                self._logger.debug('Message sent.')
