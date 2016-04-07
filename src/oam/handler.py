#-*- coding:utf-8 -*-

import base
import tornado.web
from db import session_scope
from oam.business import UserManage
from random import randint
from sqlalchemy.sql.functions import current_user
import time

class OAMbase(base.BaseHandler):
    _Cookie_UID = 'cuid'
    def initialize(self):
        base.BaseHandler.initialize(self)
        self._session = None
    def needUserInfo(self, session):
        self._session = session

    # if we need user info, we need call needUserInfo first
    def get_current_user(self):
        uid = self.get_secure_cookie(self._Cookie_UID)
        if uid and self._session:
            um = UserManage(self._session)
            self._session = None
            return um.query(uid)
        return None
    def set_secure_cookie(self, name, value):
        base.BaseHandler.set_secure_cookie(self, name, value, expires_days=None)
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
                self.title = u'重新登录 '
                self.render('login.htm', fail = True)
                
                

class ManageHandle(OAMbase):
    FieldPasswd = 'origin_passwd'
    FieldNew = 'newpasswd'
    FieldReinput = 'reinputpasswd'
    
    _COOKIE_LoginTime = 'logintime'
    def get(self):
        self.title = ''
        with session_scope() as session:
            self.needUserInfo(session)
            if not current_user:
                self.redirect('/oam/login')
            um = UserManage(session)
            self.needUserInfo(session)
            firstlogin = um.isInitPasswd(self.current_user)
            t = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(self.current_user.logintime))
            s = self.get_secure_cookie(self._COOKIE_LoginTime, t)
            
            self.render('adminhome.htm', firstlogin = firstlogin, tips = '', logintime = s)
            if not firstlogin:
                if s != t:
                    self.set_secure_cookie(self._COOKIE_LoginTime, t)
                self.current_user.logintime = int(time.time())
                

    
    def post(self):
        passwd = self.get_argument(self.FieldPasswd, '')
        np = self.get_argument(self.FieldNew, '')
        rp = self.get_argument(self.FieldReinput, '')
        if np != rp:
            self.render('adminhome.htm', firstlogin = True, tips = u'两次密码不一致')
        else:
            with session_scope() as session:
                self.needUserInfo(session)
                if not current_user:
                    self.redirect('/oam/login')
                
                um = UserManage(session)
                r = um.reset(self.get_secure_cookie(self._Cookie_UID), passwd, np)
                if r:
                    self.current_user.logintime = int(time.time())
                    self.render('adminhome.htm', firstlogin = False, tips = '')
                else:
                    self.render('adminhome.htm', firstlogin = True, tips = '原密码错误')
    
    