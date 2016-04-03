#-*- coding:utf-8 -*-
import tornado.web



class WeChatHandler(tornado.web.RequestHandler):
    def get(self, officalid):
        pass
    def post(self,officalid):
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
    
