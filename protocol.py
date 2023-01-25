import datetime
import logging
import traceback
import sys
import Queue

class Protocol:
    def __init__(self, parentDemoClss):
        self.__class_name = 'PROTOCOL'
        self.DemoClss         = parentDemoClss
        self.logger       = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")
        self.dic_msgs = {'Status'               : self.msgStatus,
                         'SetPlaza'             : self.msgSetPlaza,
                         'SetLane'              : self.msgSetLane,
                         'SetCountry'           : self.msgSetCountry,
                         'SetIssuer'            : self.msgSetIssuer,
                         'SetBeaconId'          : self.msgSetBeaconId,
                         'SetType'              : self.msgSetType,
                         'Parameters'           : self.msgParameters,
                         'set_curr_time_in_sec' : self.msgSetCurrTimeInSec,
                         'SetDSRC'              : self.msgSetDSRC}
        self.default_response_value = 'value = 2 = 0x2'
        self.ans_queue=None


    def processCommand(self, serial_msg,ans_queue):
        try:
            self.ans_queue=ans_queue
            msgFunc = self.discoverMsg(serial_msg.strip())
            if msgFunc == "Shutdown":
                self.ans_queue.put("\r\nWait Shutdown to finish...\r\n\r\n")
            elif msgFunc != None:
                msgFunc(serial_msg)
            else:
                self.ans_queue.put("error.parser.unknown_variable")
        except Exception as err:
            traceback.print_exc(sys.stdout)
            serial_msg_err = ', '.join([hex(ord(c)) for c in serial_msg])
            self.logger.info("Error on process serial command. (%s)" % serial_msg_err)
            self.logger.error(err)


    def discoverMsg(self, serial_msg):
        try:
           msg = serial_msg.strip().split(' ')[0] 
        except Exception as err:
            return None
        
        if msg in self.dic_msgs.keys():
            return self.dic_msgs.get(msg, None)
        elif serial_msg.lower()[:5] == 'sirit':
            self.DemoClss.shutdown()
            return "Shutdown"
        serial_msg_err = ', '.join([hex(ord(c)) for c in serial_msg])    
        self.logger.info("Unknown message. (%s)" % serial_msg_err)
        return None


    # Function to prepare the response
    def sendResponse(self, serial_msg_ret, msg_name):
        serial_msg_ret += self.DemoClss.default_endline_value
        lst_hex = [hex(ord(c)) for c in serial_msg_ret]
        self.logger.info('Message [%s]: "%s" (%s)' % (msg_name, serial_msg_ret.strip(), ', '.join(lst_hex)))
        self.ans_queue.put(serial_msg_ret)




    # -------------------------------------------------------------------------
    # ------------------------- HERE ARE THE MESSAGES -------------------------
    # -------------------------------------------------------------------------
    def msgStatus(self, serial_msg):
        self.logger.info("Preparing message [Status].")
        serial_msg_ret = '*S OK'
        self.sendResponse(serial_msg_ret, 'Status')


    def msgSetPlaza(self, serial_msg):
        self.logger.info("Preparing message [SetPlaza].")
        msg_value = serial_msg[serial_msg.find('SetPlaza') + len('SetPlaza'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pPlaza
        #else:
        self.DemoClss.pPlaza = msg_value
        self.logger.info("Plaza set to: %s", self.DemoClss.pPlaza)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetPlaza')


    def msgSetLane(self, serial_msg):
        self.logger.info("Preparing message [SetLane].")
        msg_value = serial_msg[serial_msg.find('SetLane') + len('SetLane'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pLane
        #else:
        self.DemoClss.pLane = msg_value
        self.logger.info("Lane set to: %s", self.DemoClss.pLane)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetLane')


    def msgSetCountry(self, serial_msg):
        self.logger.info("Preparing message [SetCountry].")
        msg_value = serial_msg[serial_msg.find('SetCountry') + len('SetCountry'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pCountry
        #else:
        self.DemoClss.pCountry = msg_value
        self.logger.info("Country set to: %s", self.DemoClss.pCountry)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetCountry')
    

    def msgSetIssuer(self, serial_msg):
        self.logger.info("Preparing message [SetIssuer].")
        msg_value = serial_msg[serial_msg.find('SetIssuer') + len('SetIssuer'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pIssuer
        #else:
        self.DemoClss.pIssuer = msg_value
        self.logger.info("Issuer set to: %s", self.DemoClss.pIssuer)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetIssuer')


    def msgSetBeaconId(self, serial_msg):
        self.logger.info("Preparing message [SetBeaconId].")
        msg_value = serial_msg[serial_msg.find('SetBeaconId') + len('SetBeaconId'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pBeaconId
        #else:
        self.DemoClss.pBeaconId = msg_value
        self.DemoClss.last_tag_read = ""
        self.logger.info("BeaconId set to: %s", self.DemoClss.pBeaconId)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetBeaconId')


    def msgSetType(self, serial_msg):
        self.logger.info("Preparing message [SetType].")
        msg_value = serial_msg[serial_msg.find('SetType') + len('SetType'):].strip()
        #if msg_value == "":
        #    serial_msg_ret = "ok %s\r\n" % self.DemoClss.pType
        #else:
        self.DemoClss.pType = msg_value
        self.logger.info("Type set to: %s", self.DemoClss.pType)
        serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, 'SetType')

    def msgSetDSRC(self, serial_msg):
        cmd='SetDSRC'
        self.logger.info("Preparing message ["+cmd+"].")
        msg_value = serial_msg[serial_msg.find(cmd) + len(cmd):].strip()
        if msg_value == "":  #for empty msg returns the status
            serial_msg_ret = "ok %s\r\n" % self.DemoClss.pDSRC
        else: #otherwise take the parameter
            self.DemoClss.pDSRC = msg_value
            self.logger.info("DSRC set to: %s", self.DemoClss.pDSRC)
            if self.DemoClss.pDSRC != "0":
                evt_cmd="setup.operating_mode=active"
            else:
                evt_cmd="setup.operating_mode=standby"
            self.DemoClss.cmd_queue.put(evt_cmd)
            serial_msg_ret = self.default_response_value
        #serial_msg_ret += "\r\nok %s" % msg_value
        self.sendResponse(serial_msg_ret, cmd)


    def msgParameters(self, serial_msg):
        self.logger.info("Preparing message [Parameters].")
        serial_msg_ret = "*S plaza= %s lane= %s country= %s issuer= %s BeaconId= %s StationType= %s DSRC= %s"
        serial_msg_ret = serial_msg_ret % (self.DemoClss.pPlaza,
                                           self.DemoClss.pLane,
                                           self.DemoClss.pCountry,
                                           self.DemoClss.pIssuer,
                                           self.DemoClss.pBeaconId,
                                           self.DemoClss.pType,
                                           self.DemoClss.pDSRC)
        self.sendResponse(serial_msg_ret, 'Parameters')


    def msgSetCurrTimeInSec(self, serial_msg):
        self.logger.info("Preparing message [set_curr_time_in_sec].")
        time_in_seconds = serial_msg[serial_msg.find('set_curr_time_in_sec') + len('set_curr_time_in_sec'):].strip()
        if time_in_seconds == "":
            reader_time = self.DemoClss.modem.getReaderTime()
            dt_fromtimestamp   = datetime.datetime.fromtimestamp(int(reader_time))
            reader_time_format = dt_fromtimestamp.strftime('%Y-%m-%dT%H:%M:%S')
            #serial_msg_ret = "ok %s (%s)\r\n" % (reader_time, reader_time_format)
            serial_msg_ret = "%s (%s)\r\n" % (reader_time, reader_time_format)
        else:
            try:
                time_in_seconds = int(time_in_seconds)
                dt_fromtimestamp   = datetime.datetime.fromtimestamp(time_in_seconds)
                reader_time_format = dt_fromtimestamp.strftime('%Y-%m-%dT%H:%M:%S')
                self.logger.info("Date and time on reader format: %s", reader_time_format)
                self.DemoClss.cmd_queue.put("info.time=%s" % reader_time_format)
                #serial_msg_ret = self.default_response_value
                # #serial_msg_ret += "\r\nok %i" % time_in_seconds
                #serial_msg_ret += "\r\n %i" % time_in_seconds
                serial_msg_ret = "value = %i = 0x%x" % (time_in_seconds,time_in_seconds) #changed @RVA 20100330
            except Exception as err:
                self.logger.info("Invalid value for seconds.")
                serial_msg_ret = "error.parser.illegal_value\r\n"
        self.sendResponse(serial_msg_ret, 'set_currr_time_in_sec')

