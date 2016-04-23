#-*- coding:utf-8 -*-

import base
import hashlib
import db
import base64
from xml.etree.ElementTree import XML
import datetime
from helper import web_log
import time
import pickle

from db import session_scope, UserSession
from wechatgw.menufeature import rootFeature

class WeChatBusiness(base.BaseBusiness):
    
    def verify(self, sig, ts, nonce, echostr):
        if not sig or not ts or not nonce or not echostr:
            return ''
        
        data = self.session.query(db.WeChatData).one_or_none()
        if not data:
            web_log.info('wechatapi: verify fail, db is not configured')
            return ''
        token = data.token
        arr = [token, ts, nonce]
        arr.sort()
        r = hashlib.sha1(''.join(arr))
        h = r.hexdigest()
        b = base64.b64encode(r.digest())
        # the sig maybe a hex string or a base64 string.
        #either is supported
        if h == sig or b == sig:
            web_log.info('wechatapi: verify success')
            return echostr
        else:
            web_log.info('remote sig:' + sig)
            web_log.info('local sig:' + h)
            web_log.info('local sig:' + b)

            web_log.info('wechatapi: verify fail')
            return ''
 
 
class WeChatMsg(base.BaseBusiness):
    def __init__(self,session, msg):
        super(WeChatMsg, self).__init__(session)
        d = XML(unicode(msg).encode('utf-8'))
        # do not check whether it is resent.
        class Data(object):
            pass
        self.data = Data()
        for x in d.iter():
            setattr(self.data, x.tag, x.text)
    
    
    def process(self):
        common = ['ToUserName', 'FromUserName','CreateTime', 'MsgType', 'MsgId']
        content = ['Content']
        pic = ['PicUrl', 'MediaId']
        voice = ['MediaId', 'Format']
        video = ['MediaId', 'ThumbMediaId']
        shortvideo = video
        loc = ['Location_X', 'Location_Y', 'Scale', 'Label']
        event = ['Event']
        for x in common:
            if not hasattr(self.data, x):
                if not hasattr(self, 'ToUserName'):
                    self.data.ToUserName = 'not set'
                if not hasattr(self, 'FromUserName'):
                    self.data.FromUserName = 'not set'
                return self.invalidFormatHandle()
        func = self.defaultHandle
        special = content
        if self.data.MsgType == 'text':
            special = content
            func = self.textHandle
        elif self.data.MsgType == 'image':
            special = pic
        elif self.data.MsgType == 'voice':
            special = voice
        elif self.data.MsgType == 'video':
            special = video
        elif self.data.MsgType == 'shortvideo':
            special = shortvideo
        elif self.data.MsgType == 'location':
            special = loc
            func = self.locationHandle
        elif self.data.MsgType == 'event':
            special = event
            if self.data.Event == 'subscribe':
                self.subscribeHandle
            elif self.data.Event == 'unsubscribe':
                pass
            elif self.data.Event == 'SCAN':
                special.extend(['EventKey','Ticket'])
            elif self.data.Event == 'LOCATION':
                special.extend(['Latitude', 'Longitude', 'Precision'])
                func = self.locationHandle
            elif self.data.Event == 'CLICK':
                special.extend(['EventKey'])
            elif self.data.Event == 'VIEW':
                special.extend(['EventKey'])
        else:
            return self.invalidFormatHandle()
        for x in special:
            if not hasattr(self.data, x):
                return self.invalidFormatHandle()
        return func()
    
    
    xmlstr = u'''
        <xml>
        <ToUserName><![CDATA[{toUser}]]></ToUserName>
        <FromUserName><![CDATA[{fromUser}]]></FromUserName>
        <CreateTime>{t}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>        
    '''
   
    def invalidFormatHandle(self):
        t = int(time.time())
        c= u'系统故障'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
       
    def defaultHandle(self):
        t = datetime.datetime.now()
        c= u'该功能暂不支持'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    
    def _textHandle(self):
        t = int(time.time())
        c= u'功能尚在完善中， 敬请关注'
        session = self.session
        u = session.query(UserSession).filter(UserSession.openid == self.data.FromUserName).one_or_none()
        if u:
            m = pickle.loads(u.sessionstr)
            objectid = 0
            if m.has_key('menuid'):
                obj = rootFeature.getFfeature(m['menuid'])
                if not obj:
                    c = u'系统错误， 系统将调整至根目录\n' + rootFeature.help()
                    objectid = rootFeature.objectid
                else:
                    objectid, c = obj.execute(self.data.FromUserName, self.data.Content)
                    
            else:
                objectid, c = rootFeature.execute(self.data.FromUserName, self.data.Content)
            m['menuid'] = objectid
            u.sessionstr = pickle.dumps(m)
            u.refreshtime = t
        else:
            objectid, c = rootFeature.execute(self.data.FromUserName, self.data.Content)
            m = dict(menuid = objectid)
            u = UserSession()
            u.openid = self.data.FromUserName
            u.createtime = t
            u.refreshtime = t
            u.sessionstr = pickle.dumps(m)
            session.add(u)
        return dict(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    def textHandle(self):
        d = self._textHandle()
        return self.xmlstr.format(**d)
    
    def locationHandle(self):
        pass
    
    def subscribeHandle(self):
        t = datetime.datetime.now()
        c= u'谢谢关注, 当前仅支持文本消息功能'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    


            

