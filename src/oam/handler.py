#-*- coding:utf-8 -*-

import base
import tornado.web
from db import session_scope
from oam.business import UserManage
from random import randint


class OAMbase(base.BaseHandler):
    _Cookie_UID = 'cuid'
    pass

#{% include *filename* %}
class LoginHandler(OAMbase):
    FieldUserName = 'username'
    FieldPasswd = 'userpasswd'
    def get(self):
        self.title = u'登录 '
        self.render('login.htm', fail = False)
        
    @tornado.web.asynchronous   
    @tornado.gen.coroutine
    def post(self):
        uname = self.get_argument(self.FieldUserName, '')
        passwd = self.get_argument(self.FieldPasswd, '')
        if not uname or not passwd:
            pass
        yield tornado.gen.sleep(randint(150,250)/100.0)
        with session_scope() as session:
            um = UserManage(session)
            u = um.login(uname, passwd)
            if u:
                self.set_secure_cookie(self._Cookie_UID, unicode(u.uid))
                self.redirect('/oam/manage')
            else:
                self.render('login.htm', fail = True)
                
                

class ManageHandle(OAMbase):
    
    def get(self):
        pass
    
    def post(self):
        pass
    
    