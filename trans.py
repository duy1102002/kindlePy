import sys
import socket
import time
import gevent
import struct
import signal
import bidict

from gevent import socket,monkey
from gevent.queue import Queue
from gevent.server import StreamServer 

import communitionC2S_pb2

monkey.patch_all()
clientTable = bidict.bidict()

class rsnd():
    def __init__(self):
            self.BUFFER = ''
            self.timeOut = 500
            self.header_format = '32sIH'
            self.header_length = struct.calcsize(self.header_format)

    def dataReceived(self,data,socket):
            self.BUFFER += data
            buffer_length = len(self.BUFFER)
            _l = ''
            while (buffer_length >= self.header_length):
                uuid,len_pb_data, len_msg_name = struct.unpack(self.header_format, self.BUFFER[:self.header_length])#_bound.ParseFromString(self.BUFFER[:8])
                print uuid,len_pb_data, len_msg_name
                if len_msg_name:
                    if len_msg_name > len(self.BUFFER[self.header_length:]):
                        print( 'not enough buffer for msg name, wait for new data coming ...   ')
                        break
                    else:
                        msg_name = struct.unpack('%ds'% len_msg_name,  self.BUFFER[self.header_length:len_msg_name + self.header_length])[0]
                        _msg =  getattr(communitionC2S_pb2, msg_name, None)
                        if _msg:
                            _request = getattr(communitionC2S_pb2, msg_name)()
                            if len_pb_data <= len(self.BUFFER[self.header_length + len_msg_name :]):
                                _request.ParseFromString(self.BUFFER[self.header_length + len_msg_name : self.header_length + len_msg_name + len_pb_data])
                                if socket.fileno > 0:
                                	clientTable[str(uuid)] = socket
                                else:
                                	del clientTable[str(uuid)]
                                print clientTable
                                self.BUFFER = self.BUFFER[self.header_length + len_msg_name + len_pb_data:]
                                buffer_length = len(self.BUFFER) 
                                continue
                            else:
                                print 'not enough buffer for pb_data, waiting for new data coming ... ',len(self.BUFFER)   
                                break
                        else:
                            print( 'no such message handler. detail:', hasattr(communitionC2S_pb2, msg_name), repr(self.BUFFER))

                            return
                else:
                    print( 'Un-supported message, no msg_name. detail:', len_msg_name)
                    self.BUFFER = ''
                    return
class serverToClient():
    BUFFER = ''
    timeOut = 500
    header_format = '32sIH'
    header_length = struct.calcsize(header_format)

    def dataSend(self,data):
        global clientTable
        print 'clientTable',clientTable
        self.BUFFER += data
        buffer_length = len(self.BUFFER)
        _l = ''
        while (buffer_length >= self.header_length):
            uuid,len_pb_data, len_msg_name = struct.unpack(self.header_format, self.BUFFER[:self.header_length])#_bound.ParseFromString(self.BUFFER[:8])
            print 'uuid:',  type(uuid),uuid,len_pb_data, len_msg_name
            if len_msg_name:
                if len_msg_name > len(self.BUFFER[self.header_length:]):
                    print( 'not enough buffer for msg name, wait for new data coming ...   ')
                    break
                else:
                    msg_name = struct.unpack('%ds'% len_msg_name,  self.BUFFER[self.header_length:len_msg_name + self.header_length])[0]
                    #_func = getattr(self.factory.service, '%s' % msg_name.lower(), None) 
                    print '###  ' + msg_name,type(msg_name)
                    _msg =  getattr(communitionC2S_pb2, msg_name, None)
                    if _msg:
                        _request = getattr(communitionC2S_pb2, msg_name)()
                        if len_pb_data <= len(self.BUFFER[self.header_length + len_msg_name :]):
                            _request.ParseFromString(self.BUFFER[self.header_length + len_msg_name : self.header_length + len_msg_name + len_pb_data])

                            sock = clientTable.get(str(uuid))
                            if sock.fileno() > 0:
                                sock.sendall(self.BUFFER[:self.header_length + len_msg_name + len_pb_data])
                            else:
                            	del clientTable[str(uuid)]
                            self.BUFFER = self.BUFFER[self.header_length + len_msg_name + len_pb_data:]
                            buffer_length = len(self.BUFFER) 
                            continue
                        else:   
                            print 'SEND not enough buffer for pb_data, waiting for new data coming ... ',len(self.BUFFER)
                            break
                    else:
                        print( 'no such message handler. detail:', hasattr(communitionC2S_pb2, msg_name), repr(self.BUFFER))

                        return
            else:
                print( 'Un-supported message, no msg_name. detail:', len_msg_name)
                self.BUFFER = ''
                return

def handle_request(conn):
    try:
        while True:
            data = conn.recv(8192)
            if not data:
                conn.shutdown(socket.SHUT_WR)
            rsndInstance = rsnd()    
            rsndInstance.dataReceived(data)            
            if not data:
                conn.shutdown(socket.SHUT_WR) 
    except Exception as  ex:
        print(ex)
    finally:
        conn.close()

def handle_request(conn,conn1):
    try:
        while True:
            data = conn.recv(1024)
            print type(data),dir(data)
            if not data:
                conn.shutdown(socket.SHUT_WR)
            conn1.sendall(data)    

            if not data:
                conn.shutdown(socket.SHUT_WR)
 
    except Exception as  ex:
        print(ex)
    finally:
        conn.close()

def handle_response(conn1):
    global clientTable
    
    try:
        while True:
            data = conn1.recv(1024)
            if not data:
                conn1.shutdown(socket.SHUT_WR)
            conn1.sendall(data) 
            print data   
                       
            #conn.send(rsndInstance.pb_construct(data))
            
 
    except Exception as  ex:
        print(ex)
    finally:
        conn1.close()

def process_shutdown(signum, greenlets):
    """
    when the process recv signal, before the process exit, gevent will kill all tasks
    """
    gevent.killall(greenlets)

def process_ignore(signum, greenlets):
    """
    when the process recv signal, before the process exit, gevent will kill all tasks
    """
    pass

#def register_sys_exit_handler(greenlets):
#    """ 
#    register signal
#    """
#    gevent.signal(signal.SIGQUIT, process_shutdown, signal.SIGQUIT, greenlets)
#    gevent.signal(signal.SIGINT, process_shutdown, signal.SIGQUIT, greenlets)
#    gevent.signal(signal.SIGTERM, process_shutdown, signal.SIGQUIT, greenlets)
#   gevent.signal(signal.SIGKILL, process_shutdown, signal.SIGQUIT, greenlets)


def from_client_to_server_accept(sock,address):
    global LOGIC_SERVER_SOCKET,clientTable
    rsndInstance = rsnd()
    while 1:
        try:
            data = sock.recv(1024)  
            if not data:
            	sock.shutdown(socket.SHUT_WR)            	
        except IOError as  ex:
            print(ex) 
            del clientTable.inv[sock]
            sock.close()
            
            return

        rsndInstance.dataReceived(data,sock) 
        if type(LOGIC_SERVER_SOCKET) == type(sock):
            LOGIC_SERVER_SOCKET.sendall(data)    


def from_server_to_server_accept(sock,address):

    global LOGIC_SERVER_SOCKET

    if LOGIC_SERVER_SOCKET == -1:

        LOGIC_SERVER_SOCKET = sock

    buffer = ''

    sTcInstance = serverToClient()

    while True:

        try:

            data = sock.recv(1024)            

        except IOError as  e:

            print(e)             

            #socket.shutdown(socket.SHUT_WR)

            LOGIC_SERVER_SOCKET = -1   

        sTcInstance.dataSend(data) 

        gevent.sleep(1)

def handle(socket, address):
     print('new connection!')

def register_sys_exit_handler():
    """ 
    register signal
    """
    gevent.signal(signal.SIGQUIT, process_shutdown, signal.SIGQUIT)
    gevent.signal(signal.SIGINT, process_shutdown, signal.SIGQUIT)
    gevent.signal(signal.SIGTERM, process_shutdown, signal.SIGQUIT)
    gevent.signal(signal.SIGKILL, process_shutdown, signal.SIGQUIT)
    #print dir(signal)
    #gevent.signal(signal.SIGPIPE, process_ignore,signal.SIG_IGN)

if __name__ == '__main__':
    #register_sys_exit_handler()
    LOGIC_SERVER_SOCKET = -1
    server_from_server = StreamServer(('127.0.0.1', 11122), from_server_to_server_accept)
    server_from_server.start()
    server_from_client = StreamServer(('127.0.0.1', 11121), from_client_to_server_accept) # creates a new server
    server_from_client.start()
    server_from_server.serve_forever()
    server_from_client.serve_forever()
    
    
    




