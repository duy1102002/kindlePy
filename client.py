import socket
import getoutip
import struct
import time
import gevent
HOST = '127.0.0.1'      #'112.126.91.52'   The remote host
PORT = 11121           # The same port as used by the server





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
        global FROMOUTER,PORTINNER,HOSTOUTER,PORTINNER
        req = ""
        if ctype == communitionC2S_pb2.LOGIN:
            req = communitionC2S_pb2.C2s_login_req()            
            print 'login'
        
        head = req.head 
        head.fromOuter = FROMOUTER
        head.fromInner = PORTINNER
        head.to = HOSTOUTER
        head.portInner = PORTINNER
        req.username = "duyong"
        print req
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
    global FROMOUTER,PORTOUTER
    fromOuter = FROMOUTER
    fromPortOuter = PORTOUTER
    print fromOuter,fromPortOuter
    if msg:
        pb_data = msg.SerializeToString()
        header_pack = 'IHIH%ds'%len(msg.__class__.__name__)
        print  'header_pack' + header_pack + '######' + msg.__class__.__name__
        _header = struct.pack('IHIH%ds'%len(msg.__class__.__name__),FROMOUTER,PORTOUTER, len(pb_data) ,len(msg.__class__.__name__), msg.__class__.__name__)
        #self.transport.write(_header + pb_data)
        print '######header'+ _header  
        return (_header + pb_data)

def socketSend(conn):
    while True:
        #msg = bytes(input(">>:"),encoding="utf8")
        originpkt = CommandFactory();
        msg = originpkt.generateCommand(communitionC2S_pb2.LOGIN);
        print  msg
        print 'aaa'
        msg = pb_construct(msg)
        print 'b' + msg
        #msg = bytes(input(">>:"))
        if msg:
            conn.sendall(msg)
        gevent.sleep(1)
        #time.sleep(1)
        #data = s.recv(1024)
        #print(data)
        #time.sleep(1)
        #print('Received', repr(data))

def socketRecv(conn):
    while True:
        #data = conn.recv(1024)
        #print(data)
        time.sleep(1)
        #print('Received', repr(data))

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #(ipInner,portInner)  = s.getsockname()
    (FROMINNER,PORTINNER) = s.getsockname()
    print type(FROMINNER),type(FROMINNER)
    ch3 = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    print type(getoutip.get_pub_ip()),getoutip.get_pub_ip()
    FROMOUTER = ch3(getoutip.get_pub_ip())
    FROMINNER = ch3(FROMINNER)
    HOSTOUTER = ch3(HOST)
    PORTOUTER = 0

    tasks = [gevent.spawn(socketSend,s)]

    gevent.joinall(tasks)