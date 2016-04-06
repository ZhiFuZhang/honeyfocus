#-*- coding:utf-8 -*-

import base
import hashlib
import db
import base64
from xml.etree.ElementTree import XML
import datetime

class WeChatBusiness(base.BaseBusiness):
    
    def verify(self, sig, ts, nonce, echostr):
        if not sig or not ts or not nonce or not echostr:
            return ''
        
        data = self.session.query(db.WeChatData).one_or_none()
        token = data.token
        arr = [token, ts, nonce]
        arr.sort()
        r = hashlib.sha1(''.join(arr))
        h = r.hexdigest()
        b = base64.encode(r.digst())
        # the sig maybe a hex string or a base64 string.
        #either is supported
        if h == sig or b == sig:
            return echostr
        else:
            return ''
 
 
class WeChatMsg(base.BaseBusiness):
    def __init__(self,session, msg):
        super(WeChatMsg, self).__init__(session)
        d = XML(msg)
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
                return None
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
            return None
        for x in special:
            if not hasattr(self.data, x):
                return None
        
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
   
    def defaultHandle(self):
        t = datetime.datetime.now()
        c= u'功能尚在完善中， 敬请关注'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    def textHandle(self):
        t = datetime.datetime.now()
        c= u'功能尚在完善中， 敬请关注'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    
    def locationHandle(self):
        pass
    
    def subscribeHandle(self):
        t = datetime.datetime.now()
        c= u'谢谢关注, 当前仅支持文本消息功能'
        return self.xmlstr.format(toUser = self.data.FromUserName, fromUser = self.data.ToUserName, t = t, content= c)
    

