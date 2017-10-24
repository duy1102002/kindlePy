import sys
import socket
import time
import gevent
import struct
import signal


from gevent import socket,monkey
from gevent.queue import Queue

monkey.patch_all()

import communitionC2S_pb2


class userInfo:
    def __init__(self,username,userid):
        self.username = username
        self.userid = userid

class CommandGrep:
    
        #if isinstance()
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
        else:
            print 'error'
        req.head = CommandHead()
        print sys.getsizeof(req)
        reg.head.generateHead(sys.getsizeof(req),ctype)


 

class rsnd():
    BUFFER = ''
    timeOut = 500
    header_format = 'IHIH'
    header_length = struct.calcsize(header_format)

    def dataReceived(self,data):
            self.BUFFER += data
            buffer_length = len(self.BUFFER)
            _l = ''
            while (buffer_length >= self.header_length):
                out_ip, out_port,len_pb_data, len_msg_name = struct.unpack(self.header_format, self.BUFFER[:self.header_length])#_bound.ParseFromString(self.BUFFER[:8])
                print out_ip, out_port,len_pb_data, len_msg_name
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
                                #reactor.callLater(0, _func, self, _request)
                                #print _request,type(_request),dir(_request) 
                                #print _request.__str__(),_request.__name__(),_request.__class__()
                                grepCommand(_request)
                                
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

    def pb_construct(self,msg):
        if msg:
            pb_data = msg.SerializeToString()
            _header = struct.pack(self.header_format + '%ds'%len(msg.__class__.__name__), len(pb_data), len(msg.__class__.__name__), msg.__class__.__name__)
            #self.transport.write(_header + pb_data)
            return (_header + pb_data)

    def grepCommand(self,cClass):
            if isinstance(_request,communitionC2S_pb2.C2s_login_req):
                loginQ.put_nowait(cClass)
                print 'isinstance'
            elif isinstance(_request,communitionC2S_pb2.C2s_register_req):
                registerQ.put_nowait(cClass)
            elif isinstance(_request,communitionC2S_pb2.C2s_modipwd):
                modipwdQ.put_nowait(cClass)
            elif isinstance(_request,communitionC2S_pb2.C2s_search_req):
                searchQ.put_nowait(cClass)
            elif isinstance(_request,communitionC2S_pb2.C2s_push_req):    
                pushBookQ.put_nowait(cClass)
            else:
                print 'error msg type'    
def handle_request(conn):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                conn.shutdown(socket.SHUT_WR)
            rsndInstance = rsnd()    
            rsndInstance.dataReceived(data)            
            #conn.send(rsndInstance.pb_construct(data))
            if not data:
                conn.shutdown(socket.SHUT_WR)
 
    except Exception as  ex:
        print(ex)
    finally:
        conn.close()

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

def processReq(pthread):
    while True:
        while not loginQ.empty():
            mission = loginQ.get()
            gevent.sleep(0)
            print 'processReq' 
            print mission
        gevent.sleep(0)
         
def processReq(pthread):
    while True:
        while not loginQ.empty():
            mission = loginQ.get()
            gevent.sleep(0)
            print 'processReq' 
            print mission
        gevent.sleep(0)
         

if __name__ == '__main__':
    #server(11121)
    HOST = '127.0.0.1'  #'112.126.91.52'    # The remote host
    PORT = 11122           # The same port as used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    recvQ = Queue()
    sendQ = Queue()
    processQ = Queue()
    loginQ = Queue()
    registerQ = Queue()
    modipwdQ = Queue()
    searchQ = Queue()
    pushBookQ = Queue()

    #fake user
    userList = dict()
    u1 = userInfo('duyong',1)
    userList['1'] = u1




 #gevent.spawn(handle_request, cli)
    tasks = [gevent.spawn(handle_request, s)
        ,gevent.spawn(processReq, 'pthread1')]
    register_sys_exit_handler(tasks)
    gevent.joinall(tasks)