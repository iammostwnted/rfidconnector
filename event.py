import datetime
import logging
import select
import socket
import threading
import time



class EventChannelStopRequestException(Exception):
    def __str__(self): return "DemoClss stop request."
    
class Event(threading.Thread):
    def __init__(self, parentDemoClss):
        threading.Thread.__init__(self)
        self.__class_name = 'EVENT'
        self.DemoClss         = parentDemoClss
        self.host         = self.DemoClss.params['HOST']
        self.port         = self.DemoClss.params['EVT_PORT']
        self.logger       = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")
        self.sock         = None
        self.evt_id       = None


    def run(self):
        while self.DemoClss.term_event.isSet():
            try:
                self.logger.info("Connecting to event channel.")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.setId()
                self.configAntenna()
                self.registerEvents()
                self.listenEvents()
            except EventChannelStopRequestException as err:
                self.logger.error(err)
                self.cleanup()
            except Exception as err:
                self.logger.error(err)
                self.cleanup()
                self.logger.info("Waiting for reconnect.")
                time.sleep(self.DemoClss.params['EVT_CONN_RETRY_STEP'])
        self.logger.info(self.__class_name.capitalize() + " object stopped.")


    def setId(self):
        input_ready, output_ready, except_ready = select.select([self.sock], [], [])
        if self.sock in input_ready:
            ret = ""
            while True:
                ret += self.sock.recv(self.DemoClss.params['EVT_BUF_SIZE'])
                if ret.find("\r\n\r\n") == -1:
                    continue
                else:
                    break
               
        self.evt_id = (ret.split('=')[1]).strip()
        self.logger.info("Event ID: %s" % self.evt_id)

    def configAntenna(self):
        self.logger.info("Configuring the parameters of the antenna")
        evt_cmd = "tag.reporting.arrive_fields = tag_id tid user_data rssi"
        self.DemoClss.cmd_queue.put(evt_cmd)
        evt_cmd = "setup.operating_mode=active"
        self.DemoClss.cmd_queue.put(evt_cmd)
        evt_cmd = "tag.reporting.arrive_generation=wait_for_tid"
        self.DemoClss.cmd_queue.put(evt_cmd)
        self.logger.info("Configuring the parameters of the antenna (xavi)")
        evt_cmd = "modem.protocol.isoc.control.set(display_tag_crc=false)"
        self.DemoClss.cmd_queue.put(evt_cmd)


    def registerEvents(self):
        self.logger.info("Registering events.")
        for evt in self.DemoClss.params['EVENTS']:
            evt_cmd = "reader.register_event(id=%s,name=%s)" % (self.evt_id, evt)
            self.DemoClss.cmd_queue.put(evt_cmd)


    def listenEvents(self):
        while True:
            ret = ""
            if not self.DemoClss.term_event.isSet():
                raise EventChannelStopRequestException
            input_ready, output_ready, except_ready = select.select([self.sock], [], [], self.DemoClss.sl_get_timeout)
            if self.sock in input_ready:
                while True:
                    ret += self.sock.recv(self.DemoClss.params['EVT_BUF_SIZE'])
                    if ret.find("\r\n\r\n") == -1:
                        continue
                    else:
                        break
                ret = ret.strip()
                self.logger.info("Event Received: %s" % ret)
                self.processEvent(ret)


    def processEvent(self, evt = ''):
        "event.tag.arrive tag_id=0x0011223344556677889900AA"
        "event.dio.in.1 value=0"
        "event.status.tx_limit_exceeded"
        try:            
            if evt != '':
                if evt[:30] == 'event.status.tx_limit_exceeded':
                    self.logger.info("Tx Timeout")
                    if self.DemoClss.pDSRC != "0":
                        evt_cmd="setup.operating_mode=active"
                        self.DemoClss.cmd_queue.put(evt_cmd)
                else:
                    msg_lst=[]
                    msg_lst= evt.split(' ')
                    evt_name=msg_lst[0]
                    dic_data = {}
                    for data in msg_lst[1:]:
                        d,v=data.split('=')
                        dic_data[d.strip()]=v.strip()
                        
                    if evt_name.find("event.tag.arrive") != -1:
                        tag_id = dic_data.get('tag_id')
                        tid = dic_data.get('tid')
                        rssi= dic_data.get('rssi')
                        user_data=dic_data.get('user_data')
                        self.logger.info("Xavi. dic_data is: %s" % (dic_data))
                        vehicle_plate='0000000000'
                        vehicle_class='00'
                        if self.DemoClss.params['EPC']:
                            tag=tag_id
                        else:
                            if len(tid)<42:  # for NXP tags TID 64 bits
                                tag=tid
                            else:
                                tag='0x'+tid[10:26] #for Higgs3 TID 192 bits

                        if tag[-1]==',':    #take the last comma
                            tag=tag[:-1]
                        
                        if len(user_data) >= 26:
                            vehicle_plate = user_data[2:26] # Used to be [2:22]. See #38483 and #30939
                            vehicle_class = user_data[26:28] # Used to be: [24:26]. See #38483 and #30939
                            
                        self.logger.info("Tag ID: %s, TID: %s, TAG: %s, VEHICLE [PLATE: %s CLASS: %s]" % (tag_id,tid,tag,vehicle_plate,vehicle_class))
                        deltat=time.time()-self.DemoClss.last_time_read
                        timeout=self.DemoClss.params['TAG_TIMEOUT']
                        if deltat>timeout or tag != self.DemoClss.last_tag_read:
                            self.logger.info("New tag found, starting process.")
                            if self.DemoClss.Validate.Validate(tag_id[2:]) == True:
                                self.DemoClss.last_tag_read = tag
                                self.DemoClss.last_time_read = time.time()
                                self.processTag(tag[2:],rssi,vehicle_plate,vehicle_class)
                            else:
                                err_msg = '*E 0 Invalid Tag Type\r\n'
                                #self.DemoClss.serial_queue.put(err_msg)
                                self.DemoClss.server_queue.put(err_msg)
                                self.logger.info("Tag not Validated.")
                        else:
                            self.logger.info("Same tag read, no report sent.")
                    
        except Exception as err:
            self.logger.info("Could not process event.")
            self.logger.error(err)

    def hextranslate(self, s):
        res = ''
        for i in range(len(s)/2):
                realIdx = i*2
                res = res + chr(int(s[realIdx:realIdx+2],16))
        return res

    def processTag(self, tag_id, rssi, vehicle_plate, vehicle_class):
        dt = datetime.datetime.now()
        if (not self.DemoClss.params['EPC'] or len(tag_id) == 24):
            
            self.logger.info("Preparing message [*I].")                        
            msg_ret  = "*I "
            msg_ret += "%s " % self.DemoClss.pPlaza                                # param_plaza
            msg_ret += "%s " % self.DemoClss.pLane                                 # param_lane
            msg_ret += "%s " % dt.strftime('%s')                                   # param_RTC
            msg_ret += "%s " % '618'                                               # tag_country
            msg_ret += "%s " % '999'                                          	   # tag_issuer
            if self.DemoClss.params['EPC']:
                if self.DemoClss.params['HEXA']:
                    msg_ret += "%s " % tag_id                              	   # hexa
                else:
                    msg_ret += "%s " % int(tag_id, 10)                             # decimal
            else:
                msg_ret+="%s " % tag_id
            msg_ret += "%s " % vehicle_class                                   # vehicle_class
            msg_ret += "%s " % '618'                                           # param_country
            msg_ret += "%s " % '0'                                             # param_issuer
            msg_ret += "%s " % '0'                                             # param_plaza
            msg_ret += "%s " % '0'                                             # param_lane
            msg_ret += "%s " % '0'                                             # param_RTC
            msg_ret += "%s " % '7'                                             # param_type
            msg_ret += "%s " % '0'                                             # tamper
            msg_ret += "%s " % '0'                                             # battery
            msg_ret += "%s " % '2'                                             # transaction_status
            msg_ret += "%s " % '618'                                           # tag_lplate_country
            msg_ret += "%s " % '1'                                             # tag_lplate_alphabet
            msg_ret += "%s " % vehicle_plate                           	       # vehicle_plate
            msg_ret += "%s"  % rssi                                            # rssi
        
            #serial_msg_ret = msg_ret + self.DemoClss.default_endline_value
            #lst_hex = [hex(ord(c)) for c in serial_msg_ret]
            #self.logger.info('Message [*I]: "%s" (%s)' % (serial_msg_ret.strip(), ', '.join(lst_hex)))
            #self.DemoClss.serial_queue.put(serial_msg_ret)
            self.DemoClss.server_queue.put(msg_ret)
            
        else:
            err_msg = '*E 0 %s Invalid Tag Length\r\n' % dt.strftime('%s')
            #self.DemoClss.serial_queue.put(err_msg)
            self.DemoClss.server_queue.put(err_msg)

    def cleanup(self):
        try:
            self.logger.info("Closing event channel.")
            self.sock.close()
        except Exception as err: pass





