import logging
import Queue
import select
import socket
import threading
import time

class ServerCtrlStopRequestException(Exception):
    def __str__(self): return "Main class stop request."

class ServerCtrl(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.__class_name    = 'SERVERCTRL'
        self.main_class      = parent
        self.srv_host        = self.main_class.params['SRV_HOST']
        self.srv_port        = self.main_class.params['SRV_PORT']
        self.srv_buf_size    = self.main_class.params['SRV_BUF_SIZE']
        self.srv_msg_term    = self.main_class.params['SRV_MSG_TERM']
        self.logger          = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")
        self.sock            = None
        self.client_sock     = None
        self.client_addr     = None
        self.sock_lock       = threading.Lock()


    def run(self):
        while self.main_class.term_event.isSet():
            try:
                self.logger.info("Binding to server port.")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.srv_host, self.srv_port))
                self.sock.listen(5)
                self.main_class.ready_signal.set()
                (self.client_sock, self.client_addr) = self.sock.accept()
                self.logger.info("Client connected: %s" % self.client_addr[0])
                self.listenServer()
            except ServerCtrlStopRequestException as err:
                self.logger.error(err)
                self.cleanup()
            except Exception as err:
                self.logger.error(err)
                self.cleanup()
                self.logger.info("Waiting for reconnect.")
                time.sleep(self.main_class.params['MDM_CONN_RETRY_STEP'])
        self.logger.info(self.__class_name.capitalize() + " object stopped.")



    def listenServer(self):
        ret = ""
        ret_temp = ""
        
        try:
            while not self.main_class.server_queue.empty():
                msg=self.main_class.server_queue.get_nowait()
        except Exception as err:
            self.logger.error(err)
            
        while self.client_sock != None:
            if not self.main_class.term_event.isSet():
                raise ServerCtrlStopRequestException
            
            input_ready, output_ready, except_ready = select.select([self.client_sock], [self.client_sock], [self.client_sock], self.main_class.sl_get_timeout)
            if self.client_sock in input_ready:
                szIn=self.client_sock.recv(self.srv_buf_size)
                if len(szIn)>0:
                    ret_temp += szIn
                    while ret_temp.find(self.srv_msg_term) != -1:
                        ret_temp = ret_temp.split(self.srv_msg_term)
                        ret = ret_temp[0].strip()
                        ret_temp = self.srv_msg_term.join(ret_temp[1:])

                        self.logger.info("Server received: %s" % ret)
                        self.processMsg(ret)
                else:
                    raise Exception('Receiving empty-closed connection')
                    
                    
            elif self.client_sock in output_ready:
                try:
                    msg = self.main_class.server_queue.get_nowait()
                    self.logger.info("Server sent: %s" % msg)
                    self.client_sock.send("%s%s" % (msg, self.srv_msg_term))
                except Queue.Empty:
                    time.sleep(0.04)
            elif self.client_sock in except_ready:
                try:
                    self.logger.error("Except situation")
                except Exception as err:
                    self.logger.error(err)
                



    def processMsg(self, ret):
        #-----------------------------------#
        # DO SOME WITH THE INCOMING MESSAGE #
        #-----------------------------------#
        self.main_class.protocol.processCommand(ret,self.main_class.server_queue)
        
        self.logger.info("Processing Message: %s" % ret)
        if ret.strip().upper() == "QUIT":
            self.cleanup()

    def cleanup(self):
        try:
            self.logger.info("Closing modem channel.")
            self.client_sock.close()
            self.sock.close()
            self.client_sock = None
            self.sock = None
        except Exception as err: pass









