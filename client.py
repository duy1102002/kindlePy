import socket
import getoutip
import struct
import time
import gevent
import uuid
from gevent import socket,monkey
from gevent.queue import Queue
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
        if ctype == communitionC2S_pb2.SEARCH:
            req = communitionC2S_pb2.C2s_search_req()            
            print 'search'
        if ctype == communitionC2S_pb2.PUSH:
            req = communitionC2S_pb2.C2s_push_req()            
            print 'push'    

        head = req.head 
        head.fromOuter = FROMOUTER
        head.fromInner = PORTINNER
        head.to = HOSTOUTER
        head.portInner = PORTINNER
        head.uuid = UUID      
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


class rsnd():
    BUFFER = ''
    timeOut = 500
    header_format = '32sIH'
    header_length = struct.calcsize(header_format)

    def dataReceived(self,data):
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
                            print _request,type(_request)
                            if len_pb_data <= len(self.BUFFER[self.header_length + len_msg_name :]):
                                _request.ParseFromString(self.BUFFER[self.header_length + len_msg_name : self.header_length + len_msg_name + len_pb_data])

                                self.grepCommand(_request)
                                
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

    def grepCommand(self,cClass):
            global step
            print cClass
            if isinstance(cClass,communitionC2S_pb2.C2s_login_req):
                #loginQ.put_nowait(cClass)
                print 'isinstance loginQ'
                
            elif isinstance(cClass,communitionC2S_pb2.C2s_register_req):
                #registerQ.put_nowait(cClass)
                pass
            elif isinstance(cClass,communitionC2S_pb2.C2s_modipwd):
                #modipwdQ.put_nowait(cClass)
                pass
            elif isinstance(cClass,communitionC2S_pb2.C2s_search_req):
                #searchQ.put_nowait(cClass)
                pass
            elif isinstance(cClass,communitionC2S_pb2.C2s_push_req):    
                #pushBookQ.put_nowait(cClass)
                pass
            elif isinstance(cClass,communitionC2S_pb2.C2s_common_rpy):
                print 'login reply',cClass
                step = 2
                #loginReplyQ.put_nowait(cClass)
            else:
                print 'error msg type'  

        

def pb_construct(msg):
    global FROMOUTER,PORTOUTER,UUID
    if msg:
        pb_data = msg.SerializeToString()
        _header = struct.pack('32sIH%ds'%len(msg.__class__.__name__),str(UUID), len(pb_data) ,len(msg.__class__.__name__), msg.__class__.__name__)  
        return (_header + pb_data)

def socketSend(conn):
    while True:
        while not commandQ.empty():
            mission = commandQ.get()
            print 'process123' 
            print mission        
            msg = pb_construct(mission) 
            if msg:
                conn.sendall(msg)
            gevent.sleep(0)   
        gevent.sleep(1)


def socketRecv(conn):
    rsndInstance = rsnd()
    while True:
        print 'receive'
        data = conn.recv(128)            
        rsndInstance.dataReceived(data)   
        gevent.sleep(0)


def createLogin():
    print 'please input username:'
    username = raw_input()
    print 'please input password:'
    password = raw_input()
    originpkt = CommandFactory();
    msg = originpkt.generateCommand(communitionC2S_pb2.LOGIN);
    msg.username = username
    msg.encryptedpwd = password
    commandQ.put_nowait(msg)
    gevent.sleep(0)

def createFind():
    print 'please input bookName:'
    bookname = raw_input()
    originpkt = CommandFactory();
    msg = originpkt.generateCommand(communitionC2S_pb2.SEARCH);
    msg.bookname = bookname
    commandQ.put_nowait(msg)
    gevent.sleep(1)

def createPush():
    print 'please input bookPath:'
    bookPath = raw_input()
    msg = originpkt.generateCommand(communitionC2S_pb2.PUSH);
    msg.bookpath = bookpath
    commandQ.put_nowait(msg)
    gevent.sleep(1)

def stepChange():
    global step
    while True:
        if step == 1 :
            createLogin()
            step = 10
        elif step == 2:
            createFind()
        else:
            pass
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
    commandQ = Queue()
    step = 1
    tasks = [gevent.spawn(socketSend,s),gevent.spawn(socketRecv,s),gevent.spawn(stepChange)]

    gevent.joinall(tasks)
