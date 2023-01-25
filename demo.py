#Lib Import
import logging
import Queue
import threading
import time
#App Import
from event import Event
from modem import Modem
from serverctrl import ServerCtrl
from protocol import Protocol
#from serialctrl import SerialCtrl
from util import Util
from ValidateEPC import Validate_EPC


threads_running = [] # Threads that main class started.

class DemoClss:
    def __init__(self, params):
        self.__class_name   = 'DemoClss'
        self.params         = params
        self.logger         = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name + " Object Created.")
        self.term_event     = threading.Event()
        self.term_event.set()
        self.util           = Util()
        self.protocol       = Protocol(self)
        self.cmd_queue      = Queue.Queue()
#        self.serial_queue   = Queue.Queue()
        self.server_queue   = Queue.Queue()
        self.last_tag_read  = ""        
        self.sl_get_timeout = self.params['SELECT_GET_TIMEOUT']
        self.pPlaza         = 0
        self.pLane          = 0
        self.pCountry       = 618
        self.pIssuer        = 0
        self.pBeaconId      = 0
        self.pType          = 7
        self.pDSRC          = 1
        self.modem          = None
        self.event          = None
        self.server         = None
        self.default_endline_value = '\r\n'
        self.Validate       = Validate_EPC()
        self.last_time_read = time.time()
        self.ready_signal = threading.Event()
        self.ready_signal.clear()


    def createChannels(self):
        self.logger.info("Creating channels threads.")
        self.modem = Modem(self)
        self.modem.setName("MODEM")
        self.modem.start()
        threads_running.append(self.modem)
        
        self.event = Event(self)
        self.event.setName("EVENT")
        self.event.start()
        threads_running.append(self.event)
        
        self.logger.info("Creating TCP-IP.")
        self.server= ServerCtrl(self)
        self.server.setName("TCPIP")
        self.server.start()
        threads_running.append(self.server)
    
# Removed Serial Support
#    def createSerialCtrl(self):
#        self.logger.info("Creating Serial Control thread.")
#        serial_ctrl = SerialCtrl(self)
#        serial_ctrl.setName("SERIALCTRL")
#        serial_ctrl.start()
#        threads_running.append(serial_ctrl)
    
    
    def shutdown(self):
#        self.logger.info("Changing serial port settings.")
        # Change settings for serial port
#        self.cmd_queue.put("com.serial.set(baudrate=115200,databits=8,parity=NONE,echo=true,stopbits=1)")
        # Give seria port time to change
#        self.logger.info("Wait for shutdown to finish.")
#        time.sleep(10)
        
#        self.logger.info("Starting up CLI application.")
        # Disable CLI.
#        self.cmd_queue.put("com.serial.console(program=CLI)")
        # Give serial port time to shutdown.
#        time.sleep(2)
        
        # Set the event to stop all threads
        self.term_event.clear()




