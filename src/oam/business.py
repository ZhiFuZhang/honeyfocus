#-*- coding:utf-8 -*-
import base.BaseBusiness
from db import *
import time
from random import randint
class UserManage(base.BaseBusiness):
    def login(self, uname, passwd):   
        u = self.session.query(User).filter(User.username == uname).one_or_none()
        if u:
            c = int(time.time())
            f = u.failtimes - 6
            f = f if f > 0 else 0
            interval = f * f  * 60
            if c >= u.logintime + interval:
                p, s = u.passwd.split(',')
                n = self.hmac(s, passwd)
                if n == p:
                    u.logintime = c
                    u.failtimes = 0
                    self.session.commit()
                    return u
                else:
                    u.logintime
                    u.failtimes = u.failtimes + 1
                    self.session.commit()
                    return None
            else:
                return None
        else:
            return None
        
    def query(self, uid):
        return self.session.query(User).filter(User.uid == uid).one_or_none()
    
    def add(self, username, passwd, power):
        salt = self.random()
        passwd = self.hmac(salt, passwd) + ',' + salt
        t = int(time.time())
        u = User(username=username, passwd = passwd, createtime = t, power = power )
        self.session.add(u)
    
    def update(self, uid, passwd, power):
        u = self.query(uid)
        if u:
            salt = self.random()
            passwd = self.hmac(salt, passwd) + ',' + salt
            t = int(time.time())
            u.passwd = passwd
            u.power = power
            self.session.commit()
            return True
        else:
            return False
    
    @staticmethod
    def init_admin(session):
        um = UserManage(session)
        um.add('superstar@honeyfocus.com', 'superwechat', 255)
    

        