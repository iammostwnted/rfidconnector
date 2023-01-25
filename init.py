#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""DemoClss-related classes and functions."""

#Lib Import
import getopt
import logging
import handlers
import os
#from serial import *
import sys
import time
import traceback
#App Import
from demo import DemoClss, threads_running

__author__    = "Pedro Riva <pedro.riva@fcmcr.com.br>"
__app_name__  = "DemoClss (DemoClss)"
__version__   = "$Revision: 1.7$"
__date__      = "6 September 2011"
__copyright__ = "Copyright (C) 2008-2009,2010,2011 Sirit Technologies. All Rights Reserved."
__credits__   = "Guido van Rossum, for an excellent programming language."

params = {'HOST'                   : '192.168.1.111',  # Reader host.
          'MDM_PORT'               : 50007,        # Modem channel port.
          'MDM_BUF_SIZE'           : 4096,         # Modem channels buffer size.
          'MDM_CONN_RETRY_STEP'    : 5,            # Modem channel retry step to reconnect.
          'EVT_PORT'               : 50008,        # Event channel port. 50008
          'EVT_BUF_SIZE'           : 1024,         # Event channels buffer size.
          'EVT_CONN_RETRY_STEP'    : 5,            # Event channel retry step to reconnect.
#          'SERIAL_PORT'            : 0,            # Serial port number.
#          'SERIAL_BAUDRATE'        : 38400,        # Serial port baudrate.
#          'SERIAL_BYTESIZE'        : EIGHTBITS,    # Serial port number of databits.
#          'SERIAL_PARITY'          : PARITY_NONE,  # Serial port parity bit.
#          'SERIAL_STOPBITS'        : STOPBITS_ONE, # Serial number of stopbits.
#          'SERIAL_TIMEOUT'         : None,         # Serial timeout, None to wait forever.
#          'SERIAL_XONXOFF'         : 0,            # Serial enable software flow control.
#          'SERIAL_RTSCTS'          : 0,            # Serial enable RTS/CTS flow control.
#          'SERIAL_WRITE_TIMEOUT'   : None,         # Serial set a timeout for writes.
#          'SERIAL_DSRDTR'          : None,         # Serial None to use rtscts setting, DSRDTR override if true or false.
#          'SERIAL_CONN_RETRY_STEP' : 5,            # Serial retry step to reconnect.
          'DEBUG_LEVEL'            : 'error',      # Debug level.
          'HEXA'                   : True,         # Assume that the tag number is in hexa instead of BCD
          'DEBUG_CONSOLE'          : False,        # Display log on console.
          'LOG_MAX_BYTES'          : 262144,       # Max of each log file in bytes. (2^16)
          'LOG_NR_FILES'           : 4,            # Nr of log files to rotate.
          'LOG_LEVELS'             : {'debug'   : logging.DEBUG,     #
                                      'info'    : logging.INFO,      # Log
                                      'warning' : logging.WARNING,   # 
                                      'error'   : logging.ERROR,     # Levels
                                      'critical': logging.CRITICAL}, #
          'EVENTS'                 : ["event.tag.arrive","event.dio.in","event.status.tx_limit_exceeded"],
                    ## Events Registered.
          'SELECT_GET_TIMEOUT'     : 5,            # Timeout for select.select and Queue.get calls.
          'SRV_HOST'               : '0.0.0.0',    # Host address
          'SRV_PORT'               : 50014,        # Listening Port
          'SRV_BUF_SIZE'           : 4096,         # Buffer size
          'SRV_MSG_TERM'           : '\r\n',       # end of command
          'TAG_TIMEOUT'            : 60,            # tag for reading same tag
          'EPC'                    : True         #if the string is formed from TAG_ID instead of TID
          }


def usage():
    help_txt = "DemoClss\n" \
               "Usage: init.py [option]\n" \
               "Options:\n" \
               "  -h, --help        Display this information\n"                                 \
               "  --version         Display application version.\n"                             \
               "  --host=<addr>     Set the IP address of the reader, defaults to localhost.\n" \
               "  --mdmport=<pnum>  Set the reader's port number for the modem channel,\n"      \
               "                    defaults to 50007.\n"                                       \
               "  --evtport=<pnum>  Set the reader's port number for the event channel,\n"      \
               "                    defaults to 50008.\n"                                       \
               "  --debug=<level>   Set the reader's debug level for the logs, defaults to\n"   \
               "                    error. Values: debug, info, warning, error, critical.\n"    \
               "  --console         Display the logs on console.\n"                             \
               "  --hexa            Assume that the tag number is hexa instead of BCD"\
               "  --epc             form the string from the tag_id instead of the TID"
    print (help_txt)


def checkOpts(params):
    try:
        #long_opts = ['help', 'version', 'host=', 'mdmport=', 'evtport=', 'debug=', 'console', 'baudrate=','hexa','epc']
        long_opts = ['help', 'version', 'host=', 'mdmport=', 'evtport=', 'debug=', 'console', 'hexa', 'epc']
        opts, args = getopt.getopt(sys.argv[1:], 'h', long_opts)
    except getopt.GetoptError as err:
        #Print help information and exit.
        print (err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o == '--version':
            print (__app_name__, __version__, __date__, '\n', __copyright__)
            sys.exit()
        elif o == '--host':
            params['HOST'] = a
        elif o == '--mdmport':
            try:
                params['MDM_PORT'] = int(a)
            except ValueError: pass
        elif o == '--evtport':
            try:
                params['EVT_PORT'] = int(a)
            except ValueError: pass
        elif o == '--debug':
            if a in ('debug', 'info', 'warning', 'error', 'critical'):
                params['DEBUG_LEVEL'] = a
        elif o == '--console':
            params['DEBUG_CONSOLE'] = True
        elif o == '--hexa':
            params['HEXA'] = True
        elif o == '--epc':
            params['EPC'] = True
#        elif o == '--baudrate':
#            try:
#                params['SERIAL_BAUDRATE'] = str(a)
#            except ValueError: pass
        else:
            assert False, 'Unhandled option'


def printOpts(params):
    logger = logging.getLogger('MAIN')
    logger.info("Starting DemoClss Application...")
    logger.info("HOST    = %(HOST)s"            % params)
    logger.info("MDMPORT = %(MDM_PORT)i"        % params)
    logger.info("EVTPORT = %(EVT_PORT)i"        % params)
    logger.info("DEBUG   = %(DEBUG_LEVEL)s"     % params)
    logger.info("CONSOLE = %(DEBUG_CONSOLE)s"   % params)
    logger.info("HEXA    = %(HEXA)s"            % params)
    logger.info("EPC     = %(EPC)s"             % params)
#    logger.info("BAUDRATE= %(SERIAL_BAUDRATE)s" % params)
    


def prepareLogger(params):
    logger = logging.getLogger('')
    logger.setLevel(params['LOG_LEVELS'][params['DEBUG_LEVEL']])
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-12s %(message)s")

    log_filename = './DemoClss.out'
    
    handler_rotating = handlers.RotatingFileHandler(log_filename,
        maxBytes    = params['LOG_MAX_BYTES'],
        backupCount = params['LOG_NR_FILES'])
    handler_rotating.setFormatter(formatter)
    logger.addHandler(handler_rotating)
    
    if params['DEBUG_CONSOLE']:
        handler_stream = logging.StreamHandler()
        handler_stream.setFormatter(formatter)
        logger.addHandler(handler_stream)


def waitThreads():
    logger = logging.getLogger('MAIN')
    t_name = ""
    for t in threads_running:
        t_name = t.getName()
        t.join()
        logger.info("Thread %s stopped." % t_name)
        

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        checkOpts(params)
        prepareLogger(params)
        printOpts(params)
        
        objDemoClss = DemoClss(params)
        objDemoClss.createChannels()
        
        #objDemoClss.logger.info("Shutting down CLI application.")
        # Disable CLI.
        #objDemoClss.cmd_queue.put("com.serial.console(program=none)")
        # Give serial port time to shutdown.
        #objDemoClss.logger.info("This can take a few seconds, please wait.")
        #time.sleep(5)
        
        #objDemoClss.logger.info("Changing serial port settings.")
        # Change settings for serial port
        #objDemoClss.cmd_queue.put("com.serial.set(baudrate=38400,databits=8,parity=NONE,echo=true,stopbits=1)")
        
        #readerParity = ''
        #if (params['SERIAL_PARITY'] == PARITY_NONE): readerParity = 'None'
        #if (params['SERIAL_PARITY'] == PARITY_EVEN): readerParity = 'Even'
        #if (params['SERIAL_PARITY'] == PARITY_ODD): readerParity =  'Odd'
        
        #objDemoClss.cmd_queue.put("com.serial.set(baudrate=" +str(params['SERIAL_BAUDRATE'])+ "," \
        #                                      "databits="+str(params['SERIAL_BYTESIZE'])+ "," \
        #                                      "parity="  +readerParity                  + "," \
        #                                      "echo=true"                  "," \
        #                                      "stopbits="+str(params['SERIAL_STOPBITS'])+ ")"  )
        # Give seria port time to change
        #objDemoClss.logger.info("Wait for startup to finish, please wait.")
        #time.sleep(5)
        
        #objDemoClss.createSerialCtrl()
        
        # Put reader to active mode.
        objDemoClss.cmd_queue.put("setup.operating_mode=active")
        #objDemoClss.cmd_queue.put("setup.operating_mode=standby")
        
        time.sleep(2)
        objDemoClss.logger.info("Startup done.\n")
        
        # Wait for other threads to close before exit.
        waitThreads()
        
        
    except SystemExit as err:
        pass
    except Exception as err:
        traceback.print_exc(sys.stdout)
        print ("\nGeneral Failure, please contact Sirit.")
        print (__app_name__, __version__, __date__)
        print (__copyright__)
        print ("Contact:", __author__)



