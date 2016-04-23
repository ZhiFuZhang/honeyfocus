#-*- coding:utf-8 -*-
import tornado.web
import tornado
import hashlib
import base64
import business
from tornado import gen
import time
from tornado.httpclient import AsyncHTTPClient
from db import session_scope
import helper
class WeChatHandler(tornado.web.RequestHandler):
    def get(self):
        ParamSignature = 'signature'
        ParamTimestamp = 'timestamp'
        ParamNonce     = 'nonce'
        ParamEchostr = 'echostr'
        sig = self.get_query_argument(ParamSignature, '')
        t   = self.get_query_argument(ParamTimestamp, '')
        nonce = self.get_query_argument(ParamNonce, '')
        echostr = self.get_query_argument(ParamEchostr, '')
        with session_scope() as session:
            w = business.WeChatBusiness(session)
            self.write(w.verify(sig, t, nonce, echostr))
   
    def post(self):  
        self.write('')
        self.flush()
        c = self.request.body
        # the msg is too large.
        if len(c) > 1024:
            self.write_error('304')
            return
        with session_scope() as session:
            m = business.WeChatMsg(session, c)
            rsp = m.process()
            self.write(rsp)
    def check_xsrf_cookie(self):
        #override the default handling, and do nothing for xsrf here
        pass
    
class WeChatToken(tornado.web.RequestHandler):
    def initialize(self):
        self.FieldAppID = 'appid'
        self.FieldSecret = 'secret'
        self.FieldToken = 'token'   
        
class WeChatTokenGet(WeChatToken): 
    def get(self):
        pass
    
class WeChatTokenInsert(WeChatToken): 
    def post(self):
        pass
    
class WeChatTokenUpdate(WeChatToken): 
    def post(self):
        pass
    
class WeChatTokenDelete(WeChatToken): 
    def post(self):
        pass
    
