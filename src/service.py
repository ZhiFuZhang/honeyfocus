#-*- coding:utf-8 -*-
import os
import tornado.ioloop
from db import session_scope, SysConfig, WeChatData
from helper import web_log
import time
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
import pickle
try:
    import fcntl
except ImportError:
    if os.name == 'nt':
        try:
            from tornado import win32_support as fcntl
        except ImportError:
            # only for test on windows
            class fcntl(object):
                LOCK_EX = 0
                LOCK_NB = 1
                @classmethod
                def flock(*args, **kargs):
                    pass
    else:
        raise

class Master(object):
    
    def __init__(self):
        self.pid =  open(os.path.realpath(__file__), "r") 
        self.servicelist= dict()
        self.master = False
    def start(self):
        try:  
            #regular service is added before lock
            # check whether need reboot every 5 minutes
            self.addService('rebootservice', RebootService.run, 5 * 60)
            fcntl.flock(self.pid, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.master = True
            #master service is added after lock
            self.addService('access token service', AccessTokenService.run, 4 * 60 + 45)
            self.addService('ip lisst fetch', IPListService.run, 4*60 + 50)
            return True 
        except IOError:
            return False
        except:  
            raise
    def isMaster(self):
        return self.master    
    #def addAsyncService(self, name, asyncmethod, seconds):
    #    f = lambda:tornado.ioloop.IOLoop.instance().spawn_callback(asyncmethod)
    #    return self.addService(name, f, seconds)
     
    
    def addService(self, name, callback, seconds):
        if (self.servicelist.has_key(name)):
            return False
        else:
            self.servicelist[name] = tornado.ioloop.PeriodicCallback(callback, seconds * 1000 * 1000)
            self.servicelist[name].start()
            return True
    def removeService(self, name):
        if (self.servicelist.has_key(name)):
            self.servicelist[name].stop()
            self.servicelist.pop(name)
            return True
        return False
    
    def stop(self):
        for x in self.servicelist:
            x.stop()
        del self.servicelist[:]
    def release(self):
        self.pid.close() 
        

class Service(object):
    @classmethod
    def instance(cls):
        name = '_instance' + str(id(cls))
        if not hasattr(cls, name): 
            setattr(cls, name, cls())
        return getattr(cls, name)

class RebootService(Service):
    def _getFalg(self):
        with session_scope() as session:
            s = session.query(SysConfig).one_or_none()
            rebootflag = 0
            if s:
                rebootflag = s.rebootflag
            else:
                rebootflag = 0
            return rebootflag
    def __init__(self):
        self.rebootflag = self._getFalg()
        
    def _run(self):
        flag = self._getFalg()
        if flag != self._getFalg():
            web_log.critical('rebootflag is changed, the rebooting will be processed soon.')
            tornado.ioloop.IOLoop.instance().stop()
    @classmethod
    def run(cls):
        if not hasattr(cls, 'obj'):
            cls.obj = cls()
        cls.obj._run()        
 
class AccessTokenService(Service):
    def __init__(self):
        self._access_token = None
        self._query_time = 0
        
    @tornado.gen.coroutine
    def _fetch(self):
        with session_scope() as session:
            d = session.query(WeChatData).slice(0, 1).one_or_none()
            if d:
                t = int(time.time())
                url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
                url = url.format(APPID = d.appid, APPSECRET = d.secret)
                http_client = AsyncHTTPClient()
                response = yield http_client.fetch(url)
                obj = json_decode(response.request.body)
                if obj.has_key('access_token') and obj.has_key('expires_in'):
                    d.access_token = obj['access_token']
                    expires_time = obj['expires_in'] + t 
                    d.expires_time = expires_time
                elif obj.has_key('errcode') and obj.has_key('errmsg'):
                    web_log.error('fetch accesstoken failed due to [%s], [%s]'%(str(obj['errcode']), obj['errmsg']))
                else:
                    web_log.error('response can NOT be decode correctly')

    @classmethod
    def run(cls):
        cls.instance()._run()
    
    @classmethod
    def get_access_token(cls):
        t = int(time.time())
        if cls.instance()._query_time + 4 * 60 < t:
            cls.instance()._query_time  = t
            with session_scope() as session:
                d = session.query(WeChatData.access_token).slice(0,1).one_or_none()
                if d:
                    cls.instance()._access_tokein = d.access_token 
        return cls.instance()._access_tokein
    
    def _run(self):
        with session_scope() as session:
            d = session.query(WeChatData).slice(0, 1).one_or_none()
            if d:
                t = int(time.time())
                expires_time = d.expires_time 
                #before timeout, fetch a new token
                if expires_time  < t + 9 * 60 :
                    tornado.ioloop.IOLoop.instance().spawn_callback(self._fetch)            
    

class IPListService(Service):
    
    def __init__(self):
        self._ip_list = None
        self._query_time = 0
        self._runtimes = 0
    def _fetch(self):
        with session_scope() as session:
            d = session.query(WeChatData.access_token).slice(0,1).one_or_none()
            if d and d.access_token:
                self._runtimes = self._runtimes + 1
                url = 'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={ACCESS_TOKEN}'
                url = url.format(ACCESS_TOKEN = d.access_token)
                http_client = AsyncHTTPClient()
                response = yield http_client.fetch(url)
                obj = json_decode(response.request.body)
                if obj.has_key('ip_list'):
                    d.iplist = pickle.dumps(obj['ip_list'])
                    IPListService._IP_LIST = obj['ip_list']
                    IPListService._Query_Time = int(time.time())
                elif obj.has_key('errcode') and obj.has_key('errmsg'):
                    web_log.error('fetch iplist failed due to [%s], [%s]'%(str(obj['errcode']), obj['errmsg']))
                else:
                    web_log.error('response can NOT be decode correctly for iplist')

    #it shall only be called by master, or after get access_token successfully
    @classmethod
    def run(cls):
        if cls.instance()._runtimes >= 150:
            cls.instance()._runtimes = 0
            tornado.ioloop.IOLoop.instance().spawn_callback(cls.instance()._fetch)

    @classmethod
    def get_ip_list(cls):
        i = cls.instance()
        t = time.time()
        if i._query_time + 30 * 60 < t:
            i._query_time = t
            with session_scope() as session:
                d = session.query(WeChatData.iplist).slice(0,1).one_or_none()
                if d and d.ip_list:
                    i._ip_list = pickle.loads(d.ip_list)
        return i._ip_list
    
    