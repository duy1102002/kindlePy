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


def dataReceived(conn,data):	
	global BUFFER
    header_format = 'IHIH'
    header_length = struct.calcsize(header_format)
    BUFFER += data
    buffer_length = len(BUFFER)
    _l = ''
    while (buffer_length >= header_length):
        len_pb_data, len_msg_name,out_ip,out_port = struct.unpack(header_format, BUFFER[:header_length])#_bound.ParseFromString(self.BUFFER[:8])
        if len_msg_name:
            if len_msg_name > len(BUFFER[header_length:]):
                print( 'not enough buffer for msg name, wait for new data coming ...   ')
                break
            else:
            	connect = clientTable.get(str(out_ip)+str(out_port))
            	if connect:
            		connect.sendall(BUFFER[0:header_length + len_msg_name + len_pb_data])
            	else:
            		print 'not found current ip' + out_ip
                BUFFER = BUFFER[header_length + len_msg_name + len_pb_data:]
                buffer_length = len(BUFFER) 
                continue

                else:
                    print( 'no such message handler. detail:', _func, hasattr(communitionC2S_pb2, msg_name), repr(BUFFER))

                    return
        else:
            print( 'Un-supported message, no msg_name. detail:', len_msg_name)
            BUFFER = ''
            return

def handle_request(conn,conn1):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                conn.shutdown(socket.SHUT_WR)
            conn1.sendall(data)    
                       
            #conn.send(rsndInstance.pb_construct(data))
            if not data:
                conn.shutdown(socket.SHUT_WR)
 
    except Exception as  ex:
        print(ex)
    finally:
        conn.close()

def handle_response(conn1):
	global clientTable
	BUFFER = ''
    try:
        while True:
            data = conn1.recv(1024)
            if not data:
                conn1.shutdown(socket.SHUT_WR)
            conn.sendall(data)    
                       
            #conn.send(rsndInstance.pb_construct(data))
            if not data:
                conn1.shutdown(socket.SHUT_WR)
 
    except Exception as  ex:
        print(ex)
    finally:
        conn1.close()

def process_shutdown(signum, greenlets):
    """
    when the process recv signal, before the process exit, gevent will kill all tasks
    """
    gevent.killall(greenlets)


def register_sys_exit_handler(greenlets):
    """ 
    register signal
    """
    gevent.signal(signal.SIGQUIT, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGINT, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGTERM, process_shutdown, signal.SIGQUIT, greenlets)
    gevent.signal(signal.SIGKILL, process_shutdown, signal.SIGQUIT, greenlets)


def func_accept(s,cli1):
    while 1:
        cs,userinfo = s.accept()
        print('come'+str(userinfo))
        print cs
        print dir(userinfo),userinfo[0],userinfo[1]
        
        ch3 = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
        clientTable[str(ch3(str(userinfo[0]))) + str(userinfo[1])] = cs
        print clientTable
        #clientTable[cs] = 
        g = gevent.spawn(handle_request,cs,cli1)

if __name__ == '__main__':
    #server(11121)
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 11121))
    s.listen(500)
    #cli, addr = s.accept()

    s1 = socket.socket()
    s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s1.bind(('0.0.0.0', 11122))
    s1.listen(500)
    cli1, addr1 = s1.accept()
    #print cli


    #gevent.spawn(handle_request, cli)
    tasks = [gevent.spawn(func_accept,s,cli1),gevent.spawn(handle_response,s,cli1)]
    register_sys_exit_handler(tasks)
    gevent.joinall(tasks)





