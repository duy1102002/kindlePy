import sys
import socket
import time
import gevent
import struct
import signal
import urllib2

from gevent import socket,monkey
from gevent.queue import Queue

monkey.patch_all()

import communitionC2S_pb2


class userInfo:
    def __init__(self,username,userid):
        self.username = username
        self.userid = userid

class CommandFactory:
    def __init__(self):
        pass
    def generateHead(self,req,length,ctype,uuid):
        req.head.length = length
        req.head.type = ctype
        req.head.uuid = uuid

    def generateCommand(self,ctype,uuid):
        req = ''
        if ctype == communitionC2S_pb2.LOGIN:
            req = communitionC2S_pb2.C2s_login_req()            
            print 'login'
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
        elif ctype == communitionC2S_pb2.LOGIN_REPLY \
        or ctype == communitionC2S_pb2.REGISTER_REPLY \
        or ctype == communitionC2S_pb2.MODIPWD_REPLY \
        or ctype == communitionC2S_pb2.PUSH_REPLY:
            req = communitionC2S_pb2.C2s_common_rpy() 
        elif ctype == communitionC2S_pb2.SEARCH_REPLY:
            req = communitionC2S_pb2.C2s_search_rpy()
        else:
            print 'error'
        
        print sys.getsizeof(req)
        self.generateHead(req,sys.getsizeof(req),ctype,uuid)
        return req


def pb_construct(msg):
    if msg:
        pb_data = msg.SerializeToString()
        _header = struct.pack(('32sIH%ds'%len(msg.__class__.__name__)),str(msg.head.uuid), len(pb_data) ,len(msg.__class__.__name__), msg.__class__.__name__) 
        print 'mark:',str(msg.head.uuid), len(pb_data) ,len(msg.__class__.__name__)
        return (_header + pb_data)


 

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
                            if len_pb_data <= len(self.BUFFER[self.header_length + len_msg_name :]):
                                _request.ParseFromString(self.BUFFER[self.header_length + len_msg_name : self.header_length + len_msg_name + len_pb_data])

                                self.grepCommand(_request)
                                
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

    def grepCommand(self,cClass):
            if isinstance(cClass,communitionC2S_pb2.C2s_login_req):
                loginQ.put_nowait(cClass)
                print 'isinstance loginQ'
            elif isinstance(cClass,communitionC2S_pb2.C2s_register_req):
                registerQ.put_nowait(cClass)
            elif isinstance(cClass,communitionC2S_pb2.C2s_modipwd):
                modipwdQ.put_nowait(cClass)
            elif isinstance(cClass,communitionC2S_pb2.C2s_search_req):
                searchQ.put_nowait(cClass)
            elif isinstance(cClass,communitionC2S_pb2.C2s_push_req):    
                pushBookQ.put_nowait(cClass)
            else:
                print 'error msg type'  



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

def processLogin(pthread):
    while True:
        while not loginQ.empty():
            mission = loginQ.get()

            print 'processLogin' 
            print mission

            originpkt = CommandFactory();
            msg = originpkt.generateCommand(communitionC2S_pb2.LOGIN_REPLY,mission.head.uuid);
            sendQ.put_nowait(msg)
        gevent.sleep(0)

def processSearch(pthread):
    while True:
        while not searchQ.empty():
            mission = searchQ.get()
            print 'processLogin' 
            print mission
            cmd = 'http://192.168.123.31:8081/find?{search:\"' + mission.bookname + '\"}'
            httpGet(cmd)
            originpkt = CommandFactory();
            msg = originpkt.generateCommand(communitionC2S_pb2.SEARCH_REPLY,mission.head.uuid);
            sendQ.put_nowait(msg)
        gevent.sleep(0)

def handle_request():
    global conn
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                conn.close()
            rsndInstance = rsnd()    
            rsndInstance.dataReceived(data)            
    except Exception as  ex:
        print(ex)
    finally:
        conn.close()


def handle_reply():
    global conn
    while True:
        while not sendQ.empty():
            msg = sendQ.get()
            msg = pb_construct(msg)
            if msg:
                conn.sendall(msg)
        gevent.sleep(0)

def handle_connection():
    global conn
    while True:        
        try:
            print 'check fileno'
            result = conn.fileno()
        except IOError as err:
            conn.close()
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                conn.connect((HOST, PORT))  
            except socket.error as msg:
                conn.close()
            print 'reconnected ,please wait ...' 
        gevent.sleep(5) 

def httpGet(url):
    print('GET: %s' % url)
    resp = urllib2.urlopen(url)
    data = resp.read()
    print('%d bytes received from %s.' % (len(data), url))

if __name__ == '__main__':
    #server(11121)
    HOST = '127.0.0.1'  #'112.126.91.52'    # The remote host
    PORT = 11122           # The same port as used by the server

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((HOST, PORT))  
    except socket.error as msg:
        conn.close()
        
    recvQ = Queue()
    sendQ = Queue()
    processQ = Queue()
    loginQ = Queue()
    registerQ = Queue()
    modipwdQ = Queue()
    searchQ = Queue()
    pushBookQ = Queue()

 #gevent.spawn(handle_request, cli)
    tasks = [gevent.spawn(handle_request)
        ,gevent.spawn(processLogin, 'pthread1')
        ,gevent.spawn(processSearch, 'pthread2')
        ,gevent.spawn(handle_reply)
        ,gevent.spawn(handle_connection)]
    register_sys_exit_handler(tasks)
    gevent.joinall(tasks)
