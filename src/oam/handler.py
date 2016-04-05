#-*- coding:utf-8 -*-

import base
import tornado.web
from db import session_scope
from oam.business import UserManage
from random import randint

class OAMbase(base.BaseHandler):
    pass  

#{% include *filename* %}
class LoginHandler(OAMbase):
    FieldUserName = 'username'
    FieldPasswd = 'userpasswd'
    def get(self):
        self.title = u'登录 '
        self.render('login.htm')
        
    @tornado.web.asynchronous   
    @tornado.gen.coroutine
    def post(self):
        self.write('')
        uname = self.get_argument(self.FieldUserName, '')
        passwd = self.get_argument(self.FieldPasswd, '')
        if not uname or not passwd:
            pass
        yield tornado.gen.sleep(randint(150,250)/100.0)
        with session_scope() as session:
            um = UserManage(session)
            u = um.login(uname, passwd)
            if u:
                pass
            else:
                pass
                
                
        
            
        
        #yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + 5)


    
    