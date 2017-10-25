import socket
import getoutip
import struct
import time
import gevent
import uuid
from gevent import socket,monkey
HOST = '127.0.0.1'      #'112.126.91.52'   The remote host
PORT = 11121           # The same port as used by the server



monkey.patch_all()


import communitionC2S_pb2

clientTable = dict()

class CommandHead:
    def __init__(self):
        pass
    def generateHead(self,length,ctype):
        global FROMOUTER,PORTINNER,FROMINNER,HOST
        head = communitionC2S_pb2.C2s_Head()
        head.length = length
        head.type = ctype
        head.fromOuter = FROMOUTER
        head.fromInner = PORTINNER
        head.to = HOSTOUTER
        head.portInner = PORTINNER
        return head


class CommandFactory:
    def __init__(self):
        pass
    def generateCommand(self,ctype):
        global FROMOUTER,PORTINNER,HOSTOUTER,PORTINNER,UUID
        req = ""
        if ctype == communitionC2S_pb2.LOGIN:
            req = communitionC2S_pb2.C2s_login_req()            
            print 'login'
        
        head = req.head 
        head.fromOuter = FROMOUTER
        head.fromInner = PORTINNER
        head.to = HOSTOUTER
        head.portInner = PORTINNER
        
        head.uuid = UUID
        req.username = "duyong"

        
        return req
        #req.head.generateHead(len(req.SerializeToString()),ctype)
'''
        elif ctype == communitionC2S_pb2.REGISTER:
            req = communitionC2S_pb2.C2s_register_req()
            print 'register'
        elif ctype == communitionC2S_pb2.MODIPWD:
            req = communitionC2S_pb2.C2s_modipwd()
            print 'modipwd'
        elif ctype == communitionC2S_pb2.SEARCH:
            req = communitionC2S_pb2.C2s_search_req()
            print 'search'
        elif ctype == communitionC2S_pb2.PUSH:
            req = communitionC2S_pb2.C2s_push_req()
            print 'push'
        else:
            print 'error'
'''

        

def pb_construct(msg):
    global FROMOUTER,PORTOUTER,UUID
    if msg:
        pb_data = msg.SerializeToString()
        _header = struct.pack('32sIH%ds'%len(msg.__class__.__name__),str(UUID), len(pb_data) ,len(msg.__class__.__name__), msg.__class__.__name__)  
        return (_header + pb_data)

def socketSend(conn):
    while True:
        originpkt = CommandFactory();
        msg = originpkt.generateCommand(communitionC2S_pb2.LOGIN);
        msg = pb_construct(msg) 
        if msg:
            conn.sendall(msg)
        gevent.sleep(1)


def socketRecv(conn):
    while True:
        data = conn.recv(512)
        print'!!!!!!recv:'
        gevent.sleep(0)

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    (FROMINNER,PORTINNER) = s.getsockname()
    print type(FROMINNER),type(FROMINNER)
    ch3 = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    print type(getoutip.get_pub_ip()),getoutip.get_pub_ip()
    FROMOUTER = ch3(getoutip.get_pub_ip())
    FROMINNER = ch3(FROMINNER)
    HOSTOUTER = ch3(HOST)
    PORTOUTER = 0
    UUID = uuid.uuid1().hex
    print type(UUID)
    tasks = [gevent.spawn(socketSend,s),gevent.spawn(socketRecv,s)]

    gevent.joinall(tasks)
