#-*- coding:utf-8 -*-
import tornado.web
import globalsetting
import os
import base64
import hashlib
import hmac
class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.title = u'无 标题'
    
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