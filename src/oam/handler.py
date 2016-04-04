#-*- coding:utf-8 -*-

import basehandler

class OAMbase(basehandler.BaseHandler):
    pass  

#{% include *filename* %}
class LoginHandler(OAMbase):
    FieldUserName = 'username'
    FieldPasswd = 'userpasswd'
    def get(self):
        self.title = u'登录 '
        self.render('login.htm')
    
    def post(self):
        user = self.get_argument(self.FieldUserName, '')
        passwd = self.get_argument(self.FieldPasswd, '')

    
    