import logging
import Queue
import select
import socket
import threading
import time

class ModemChannelStopRequestException(Exception):
    def __str__(self): return "DBTrans stop request."

class Modem(threading.Thread):
    def __init__(self, parentDBTrans):
        threading.Thread.__init__(self)
        self.__class_name = 'MODEM'
        self.DBTrans         = parentDBTrans
        self.host         = self.DBTrans.params['HOST']
        self.port         = self.DBTrans.params['MDM_PORT']
        self.logger       = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")
        self.sock         = None


    def run(self):
        while self.DBTrans.term_event.isSet():
            try:
                self.logger.info("Connecting to modem channel.")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.processCmdQueue()
            except ModemChannelStopRequestException, err:
                self.logger.error(err)
                self.cleanup()
            except Exception, err:
                self.logger.error(err)
                self.cleanup()
                self.logger.info("Waiting for reconnect.")
                time.sleep(self.DBTrans.params['MDM_CONN_RETRY_STEP'])
        self.logger.info(self.__class_name.capitalize() + " object stopped.")
                
                
    def getReaderTime(self):
        self.logger.info("Getting reader time.")
            
        input_ready, output_ready, except_ready = select.select([], [self.sock], [])
        if self.sock in output_ready:
            self.sock.send("info.time\r\n")
            
            ret = ""
            while True:
                ret += self.sock.recv(self.DBTrans.params['MDM_BUF_SIZE'])
                if ret.find("\r\n\r\n") == -1:
                    continue
                else:
                    break
                
            self.logger.info("Return: %s" % ret.strip())
            
            ret = ret.split(' ')[1].strip()
            self.logger.info("Return: %s" % ret)
            self.logger.info("Return: %s" % ret[:-4])
            ret = time.strftime('%s', time.strptime(ret[:-4], '%Y-%m-%dT%H:%M:%S'))
            return ret


    def processCmdQueue(self):
        while True:
            command = ""
            try :
                command = self.DBTrans.cmd_queue.get(True, self.DBTrans.sl_get_timeout)
            except Queue.Empty:
                if not self.DBTrans.term_event.isSet():
                    raise ModemChannelStopRequestException
                continue
                
            self.logger.info("Command: %s" % command)
                
            input_ready, output_ready, except_ready = select.select([], [self.sock], [])
            if self.sock in output_ready:
                self.sock.send(command + "\r\n")
                
                ret = ""
                while True:
                    ret += self.sock.recv(self.DBTrans.params['MDM_BUF_SIZE'])
                    if ret.find("\r\n\r\n") == -1:
                        continue
                    else:
                        break
                    
                self.logger.info("Return: %s" % ret.strip())


    def cleanup(self):
        try:
            self.logger.info("Closing modem channel.")
            self.sock.close()
        except Exception, err: pass









