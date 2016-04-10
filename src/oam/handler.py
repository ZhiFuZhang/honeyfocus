#-*- coding:utf-8 -*-

import base
import tornado.web
from oam.business import UserManage
from random import randint
from sqlalchemy.sql.functions import current_user
import time
from oam import business


class OAMbase(base.BaseHandler):
    _COOKIE_LoginTime = 'xlogintime'
    _Cookie_UID = 'cuid'
    # if we need user info, we need call needUserInfo first
    def get_current_user(self):
        uid = self.get_secure_cookie(self._Cookie_UID)
        if uid:
            um = UserManage(self.session)
            return um.query(uid)
        return None
    def get_login_url(self):
        return '/oam/login'
    def set_secure_cookie(self, name, value):
        base.BaseHandler.set_secure_cookie(self, name, value, expires_days=None)
#{% include *filename* %}
class LoginHandler(OAMbase):
    FieldUserName = 'username'
    FieldPasswd = 'userpasswd'
    def get(self):
        self.title = u'登录 '
        self.clear_cookie(self._COOKIE_LoginTime)
        self.render('login.htm', fail = False)
        
    @tornado.gen.coroutine
    def post(self):
        uname = self.get_argument(self.FieldUserName, '')
        passwd = self.get_argument(self.FieldPasswd, '')
        if not uname or not passwd:
            pass
        #sleep for 1.5 ~ 2.5 seconds, to avoid time attack
        yield tornado.gen.sleep(randint(150,250)/100.0)
  
        um = UserManage(self.session)
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
    
    @tornado.web.authenticated
    def get(self):
        self.title = ''

        if not current_user:
            self.redirect('/oam/login')
        um = UserManage(self.session)
        
        firstlogin = um.isInitPasswd(self.current_user)
        s = self.get_secure_cookie(self._COOKIE_LoginTime)
       
        if not s:
            if self.current_user.logintime == 0:
                t = u'未登录过'
            else:
                t = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(self.current_user.logintime))
            
            self.set_secure_cookie(self._COOKIE_LoginTime, t)
            self.current_user.logintime = int(time.time())
            s = t
        
        self.render('adminhome.htm', firstlogin = firstlogin, tips = '', logintime = s)    

    @tornado.web.authenticated
    def post(self):
        passwd = self.get_argument(self.FieldPasswd, '')
        np = self.get_argument(self.FieldNew, '')
        rp = self.get_argument(self.FieldReinput, '')
        if np != rp:
            self.render('adminhome.htm', firstlogin = True, tips = u'两次密码不一致')
        else:
            um = UserManage(self.session)
            r = um.reset(self.get_secure_cookie(self._Cookie_UID), passwd, np)
            if r:
                self.redirect('/oam/manage')
            else:
                self.render('adminhome.htm', firstlogin = True, tips = '原密码错误', logintime = None)
    

class WeChatConfigHandle(OAMbase):
    FieldAppId = 'wechatappid'
    FieldSecret = 'wechatsecret'
    FieldToken = 'wechattoken'
    def get(self):
        s = business.WeChatConf(self.session)
        wechatdata = s.query()
        self.render('adminwechat_update.htm', data= wechatdata, tips='')

    def post(self):
        appid = self.get_argument(self.FieldAppId)
        secret = self.get_argument(self.FieldSecret)
        token = self.get_argument(self.FieldToken)
        if not appid or not secret or not token:
            self.render('adminwechat_update.htm', data= None, tips= u'不允许空值')

        s = business.WeChatConf(self.session)
        data = s.update(appid, secret, token)
        
        self.render('adminwechat_view.htm', data = data, tips=u'设置成功')  