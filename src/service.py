#-*- coding:utf-8 -*-
import os
try:
    import fcntl
except ImportError:
    if os.name == 'nt':
        try:
            from tornado import win32_support as fcntl
        except ImportError:
            # only for test on windows
            class fcntl(object):
                def flock(self, *args, **kargs):
                    pass
    else:
        raise

class Master(object):
    
    def __init__(self):
        self.pid =  open(os.path.realpath(__file__), "r") 
    
    def lock(self):
        try:  
            fcntl.flock(self.pidfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True 
        except:  
            return False
        
    def release(self):
        self.pid.close() 
        

class Service(object):
    pass

 
class AccessTokenService(Service):
    pass
 

class IPListService(Service):
    pass
