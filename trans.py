import sys
import socket
import time
import gevent
import struct
import signal

from gevent import socket,monkey
from gevent.queue import Queue
from gevent.server import StreamServer 

import communitionC2S_pb2

monkey.patch_all()
clientTable = dict()

class rsnd():
    BUFFER = ''
    timeOut = 500
    header_format = '32sIH'
    header_length = struct.calcsize(header_format)

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

                                clientTable[str(uuid)] = socket
                                print clientTable
                                self.BUFFER = self.BUFFER[self.header_length + len_msg_name + len_pb_data:]
                                buffer_length = len(self.BUFFER) 
                                continue
                            else:   
                                print( 'not enough buffer for pb_data, waiting for new data coming ... ')
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
        print 'clientTable',dir(clientTable),clientTable
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
                            if sock != None:
                                sock.sendall(self.BUFFER[:self.header_length + len_msg_name : self.header_length + len_msg_name + len_pb_data])
                            self.BUFFER = self.BUFFER[self.header_length + len_msg_name + len_pb_data:]
                            buffer_length = len(self.BUFFER) 
                            continue
                        else:   
                            print( 'not enough buffer for pb_data, waiting for new data coming ... ')
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
            data = conn.recv(1024)
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

def register_sys_exit_handler(greenlets):
    """ 
    register signal
    """
    gevent.signal(signal.SIGQUIT, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGINT, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGTERM, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGKILL, process_shutdown, signal.SIGQUIT, greenlets)


def from_client_to_server_accept(socket,address):
    global LOGIC_SERVER_SOCKET
    while 1:
        try:
            data = socket.recv(1024)            
        except IOError as  ex:
            print(ex) 
            socket.shutdown(socket.SHUT_WR)

        rsndInstance = rsnd()    
        rsndInstance.dataReceived(data,socket) 
        if type(LOGIC_SERVER_SOCKET) == type(socket):
            LOGIC_SERVER_SOCKET.sendall(data)    


def from_server_to_server_accept(socket,address):
    global LOGIC_SERVER_SOCKET
    if LOGIC_SERVER_SOCKET == -1:
        LOGIC_SERVER_SOCKET = socket
    buffer = ''
    while True:
        try:
            data = socket.recv(1024)            
        except IOError as  e:
            print(e)             
            #socket.shutdown(socket.SHUT_WR)
            LOGIC_SERVER_SOCKET = -1

        sTcInstance = serverToClient()    
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
    gevent.signal(signal.SIGPIPE, process_ignore,signal.SIG_IGN)

if __name__ == '__main__':
    register_sys_exit_handler()
    LOGIC_SERVER_SOCKET = -1
    server_from_server = StreamServer(('127.0.0.1', 11122), from_server_to_server_accept)
    server_from_server.start()
    server_from_client = StreamServer(('127.0.0.1', 11121), from_client_to_server_accept) # creates a new server
    server_from_client.start()
    server_from_server.serve_forever()
    server_from_client.serve_forever()
    
    
    




