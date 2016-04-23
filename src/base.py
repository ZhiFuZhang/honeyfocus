#-*- coding:utf-8 -*-
import tornado.web
import globalsetting
import os
import base64
import hashlib
import hmac
from db import Session, SessionCounter
from helper import web_log
import functools


def session_run(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):        
        self.session = Session()
        SessionCounter.on_create()
        web_log.debug('session created')
        try:
            ret = method(self, *args, **kwargs)            
            if ret is not None:
                yield ret
            web_log.debug('session commit')
            self.session.commit()
        except:
            web_log.debug('session  rollback')
            self.session.rollback()
            self.set_status('509', "Database operation failed") 
        finally:
            web_log.debug('session  close')
            SessionCounter.on_close()
            self.session.close()
            del self.session
    return tornado.gen.coroutine(wrapper)

class BaseHandler(tornado.web.RequestHandler):    
    @session_run
    def get(self, *args, **kwargs):
        self.protect = True
        return self._get(*args, **kwargs)
    @session_run       
    def post(self, *args, **kwargs):
        self.protect = True
        return self._post(*args, **kwargs)
    
    def _get(self, *args, **kwargs):
        raise Exception('not implemented')
    
    def _post(self, *args, **kwargs):
        raise Exception('not implemented')
    
    
    def prepare(self):
        self.title = u'无 标题'
        #used to avoid subclass overriding  the 'get'/'post' method
        self.protect = False
            
    def on_finish(self):
        if not self.protect:
            raise Exception('DO NOT override get/post method, override the _get/_post instead !')

    def render(self, template_name, **kwargs):
        k = dict(isLocalJS = globalsetting.gIfLocalJS)
        k.update(kwargs)
        tornado.web.RequestHandler.render(self, template_name, **k)

class BaseBusiness(object):
    def __init__(self, session):
        self.session = session
    
    @staticmethod
    def random(size = 32):
        size = size if size > 9 else 9
        return base64.b64encode(os.urandom(size))[3:3+size]
    
    @staticmethod
    def hmac(salt, msg):
        if isinstance(salt, unicode):
            salt = salt.encode('ascii')
        if isinstance(salt, unicode):
            msg = msg.encode('ascii')
        h = hmac.new(salt, msg, hashlib.sha256)
        return base64.b64encode(h.digest())
    
               
class Mainhander(BaseHandler):
    def _get(self):
        self.render('adminbase.htm')