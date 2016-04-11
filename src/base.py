#-*- coding:utf-8 -*-
import tornado.web
import globalsetting
import os
import base64
import hashlib
import hmac
from db import Session
from helper import web_log

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.title = u'无 标题'
        self.session = Session()
        self.session_finished = False
        web_log.debug('create session')
    
    # for insert case,  it is better to commit the session in get/post method.
    def finish(self, chunk=None):
        if hasattr(self, 'session'):
            try:
                web_log.debug('commit session')
                self.session.commit()
            except Exception as e:
                web_log.debug('rollback session')
                self.session.rollback()
                web_log.error(e.orig)
        super(BaseHandler, self).finish(chunk)
        
    def on_finish(self):
        web_log.debug('close session')
        self.session.close()
        del self.session

    
    def render(self, template_name, **kwargs):
        k = dict(isLocalJS = globalsetting.gIfLocalJS)
        k.update(kwargs)
        tornado.web.RequestHandler.render(self, template_name, **k)

class BaseBusiness(object):
    def __init__(self, session):
        self.session = session
    
    @staticmethod
    def random(size = 32):
        return base64.b64encode(os.urandom(size + 2))[3:3+size]
    
    @staticmethod
    def hmac(salt, msg):
        if isinstance(salt, unicode):
            salt = salt.encode('ascii')
        if isinstance(salt, unicode):
            msg = msg.encode('ascii')
        h = hmac.new(salt, msg, hashlib.sha256)
        return base64.b64encode(h.digest())
    
               
class Mainhander(BaseHandler):
    def get(self):
        self.render('adminbase.htm')