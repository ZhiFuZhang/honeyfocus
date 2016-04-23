#-*- coding:utf-8 -*-

import testbase
import unittest
from wechatgw.menufeature import rootFeature, BookMarkFeature
from wechatgw.business import  WeChatMsg
from db import session_scope, BookMark, UserSession
from unittest.suite import TestSuite
from inspect import isclass
import pickle
from xml.etree.ElementTree import XML

class RootFeatureTestInit(testbase.BaseTestCase):

    def test_init(self):
        i = 0
        for x in rootFeature.featurelist:
            self.assertEqual(i,x.objectid, 'objectid' + str(x.objectid) + 'name:' + x.name)
            i = i + 1

    def test_invalid(self):

        openid = '1234'
        content = 'content'
        objid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature.help(), 'msg' + msg)
    
    def test_over(self):
        openid = '1234'
        content = '3'
        objid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature._InvalidTips+ rootFeature.help(), 'msg' + msg)
    
    def test_parent(self):
        openid = '1234'
        content = '../'
        
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature.help(), 'msg' + msg)
    def test_help(self):
        openid = '1234'
        content = '?'
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature.help(), 'msg' + msg) 
               
    def test_root(self):
        openid = '1234'
        content = '~'
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature.help(), 'msg' + msg)

    #bookmark    
    def test_0(self):
        openid = '1234'
        content = '0'
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.sub[0].objectid, 'objectid'+str(objectid))
        self.assertEqual(msg, rootFeature.sub[0].help(), 'msg' + msg)
    #version
    def test_1(self):
        openid = '1234'
        content = '1'
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.objectid, 'objectid' + str(objectid))
        #self.assertEqual(msg, '', 'msg' + msg)


class BookMarkFeatureTest(testbase.BaseTestCase):
    def afterSetup(self):
        self.objectid = rootFeature.execute('openid', '0')[0]
        self.obj = rootFeature.getFfeature(self.objectid)
        self.openid = 'openid'
    def test_invalid(self):
        content = '23jkd'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid, 'objectid:'+ str(objectid))
        self.assertEqual(msg, self.obj._InvalidTips + self.obj.help(), 'msg:' + msg)

    def test_list(self):
        for content in ('0', '1', '2', '3'):
            objectid, msg = self.obj.execute(self.openid, content)
            self.assertNotEqual(objectid, self.objectid)
            newobj = rootFeature.getFfeature(objectid)
            self.assertNotEqual(None, newobj)

    def test_parent(self):
        openid = '1234'
        content = '../'
        
        objectid, msg = self.obj.execute(openid, content)
        self.assertEqual(objectid, self.obj.parent.objectid, 'objectid')
        self.assertEqual(msg, self.obj.parent.help(), 'msg' + msg)
    def test_help(self):
        openid = '1234'
        content = '?'
        objectid, msg = self.obj.execute(openid, content)
        self.assertEqual(objectid, self.obj.objectid, 'objectid')
        self.assertEqual(msg, self.obj.help(), 'msg' + msg) 
               
    def test_root(self):
        openid = '1234'
        content = '~'
        objectid, msg = rootFeature.execute(openid, content)
        self.assertEqual(objectid, rootFeature.objectid, 'objectid')
        self.assertEqual(msg, rootFeature.help(), 'msg' + msg)
 
 
class BookMarkSearchTest(testbase.BaseTestCase):
    def beforeSetup(self):
        #self.dbecho = True
        pass
    def afterSetup(self):
        self.openid = 'openyou'
        objectid = rootFeature.execute(self.openid, '0')[0]
        obj = rootFeature.getFfeature(objectid)
        self.assertNotEqual(None, obj)
        self.assertEqual(obj.name, BookMarkFeature.Name, 'msg:'+ obj.name)

        objectid, msg = obj.execute(self.openid, '0')
        self.obj = rootFeature.getFfeature(objectid)
        self.assertNotEqual(None, self.obj)            
        self.assertEqual(self.obj.name, BookMarkFeature.SearchAction.Name, 'msg:'+ self.obj.name)

        self.record1 = u'手机号:137892383874'
        self.record2 = u'QQ号:1379987878'
        self.record3 = u'QQ号:137%998%xyz%123'
        with session_scope() as session:
            for x in(self.record1, self.record2, self.record3):
                a = BookMark(openid=self.openid, content=x)
                session.add(a)
            
    def test_normal(self):
        content = '137'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        self.assertNotEqual(-1, msg.find(self.record1))
        self.assertNotEqual(-1, msg.find(self.record2))
        
    
    def test_norecord(self):
        content = '139'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        self.assertEqual(-1, msg.find(self.record1))
        self.assertEqual(-1, msg.find(self.record2))
        
    def test_largerecord(self):
        records =(u'abcdefg', u'a啊', u'哈a', u'大a5', u'7他a', u'9uja五0', 
                        u'sldkasdfk个', u'起来a人们', u'00a11', u'22a33', u'bbacc', u'ddaee',u'过aa',u'aaa',u'ca',u'就da')
               
        with session_scope() as session:
            for x in records:
                a = BookMark(openid=self.openid, content=x)
                session.add(a)
        #new search
        content = 'a' 
        expected = ''
        objectid, msg = self.obj.execute(self.openid, content)
        expected = u'''<a>搜索结果如下：
#4.abcdefg
#5.a啊
#6.哈a
#7.大a5
#8.7他a
#9.9uja五0
#10.sldkasdfk个
#11.起来a人们
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(objectid, self.obj.objectid)
        self.assertEqual(msg, expected, msg)
        #next page
        content = '.'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''<a>搜索结果如下：
#11.起来a人们
#12.00a11
#13.22a33
#14.bbacc
#15.ddaee
#16.过aa
#17.aaa
#18.ca
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(msg, expected, msg)
        #next page
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''<a>搜索结果如下：
#18.ca
#19.就da
'''
        self.assertEqual(msg, expected, msg)
        # another new search
        content = 'a' 
        expected = ''
        objectid, msg = self.obj.execute(self.openid, content)
        expected = u'''<a>搜索结果如下：
#4.abcdefg
#5.a啊
#6.哈a
#7.大a5
#8.7他a
#9.9uja五0
#10.sldkasdfk个
#11.起来a人们
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(objectid, self.obj.objectid)
        self.assertEqual(msg, expected, msg)

    def test_largerecord2(self):
        records =(u'abcdefg', u'a啊', u'哈a', u'大a5', u'7他a', u'9uja五0', 
                        u'sldkasdfk个', u'起来a人们', u'00a11', u'22a33', u'bbacc', u'ddaee',u'过aa',u'aaa',u'ca',u'就da')
               
        with session_scope() as session:
            for x in records:
                a = BookMark(openid=self.openid, content=x)
                session.add(a)
        #new search
        content = 'a' 
        expected = ''
        objectid, msg = self.obj.execute(self.openid, content)
        expected = u'''<a>搜索结果如下：
#4.abcdefg
#5.a啊
#6.哈a
#7.大a5
#8.7他a
#9.9uja五0
#10.sldkasdfk个
#11.起来a人们
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(objectid, self.obj.objectid)
        self.assertEqual(msg, expected, msg)
        #next page
        content = '13'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''<13>搜索结果如下：
#1.手机号:137892383874
#2.QQ号:1379987878
#3.QQ号:137%998%xyz%123
'''
        self.assertEqual(msg, expected, msg)
        #next page
        content = '.'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''没有找到关键字<.>相关的内容'''
        self.assertEqual(msg, expected, msg)

       
    def test_largerecord3(self):
        records =(u'abcdefg', u'a啊', u'哈a', u'大a5', u'7他a', u'9uja五0', 
                        u'sldkasdfk个', u'起来a人们', u'00a11', u'22a33', u'bbacc', u'ddaee',u'过aa',u'aaa',u'ca',u'就da')
               
        with session_scope() as session:
            for x in records:
                a = BookMark(openid=self.openid, content=x)
                session.add(a)
        #new search
        content = 'a' 
        expected = ''
        objectid, msg = self.obj.execute(self.openid, content)
        expected = u'''<a>搜索结果如下：
#4.abcdefg
#5.a啊
#6.哈a
#7.大a5
#8.7他a
#9.9uja五0
#10.sldkasdfk个
#11.起来a人们
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(objectid, self.obj.objectid)
        self.assertEqual(msg, expected, msg)
        #next page
        content = '.'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''<a>搜索结果如下：
#11.起来a人们
#12.00a11
#13.22a33
#14.bbacc
#15.ddaee
#16.过aa
#17.aaa
#18.ca
{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'''
        self.assertEqual(msg, expected, msg)
        
        #new search
        content = u'13'
        objectid, msg = self.obj.execute(self.openid, content)
        self.assertEqual(objectid, self.obj.objectid)
        expected = u'''<13>搜索结果如下：
#1.手机号:137892383874
#2.QQ号:1379987878
#3.QQ号:137%998%xyz%123
'''
        self.assertEqual(msg, expected, msg)
 

class BookMarkAddTest(testbase.BaseTestCase):
    def afterSetup(self):
        self.openid = 'openyou'
        objectid = rootFeature.execute(self.openid, '0')[0]
        obj = rootFeature.getFfeature(objectid)
        self.assertNotEqual(None, obj)
        self.assertEqual(obj.name, BookMarkFeature.Name, 'msg:'+ obj.name)

        objectid, msg = obj.execute(self.openid, '1')
        self.obj = rootFeature.getFfeature(objectid)
        self.assertNotEqual(None, self.obj)            
        self.assertEqual(self.obj.name, BookMarkFeature.AddAction.Name, 'msg:'+ self.obj.name)

    def test_normal(self):
        content = 'addtest'
        objectid, msg = self.obj.execute(self.openid, content)    
        self.assertEqual(objectid, self.obj.objectid)
   
                  
#VersionFeature only have one layer, no test here
#class VersionFeatureTest


class WeChatTextMsgTest(testbase.BaseTestCase):
    class Data(object):
        pass
    
    xmlstr = u'''
    <xml>
 <ToUserName><![CDATA[{toUser}]]></ToUserName>
 <FromUserName><![CDATA[{fromUser}]]></FromUserName> 
 <CreateTime>{t}</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[{content}]]></Content>
 <MsgId>{msgid}</MsgId>
 </xml>
    '''
    def test_first(self):
        c = u'0'
        openid = '5678'
        touser = '1234'
        data = self.xmlstr.format(toUser=touser, fromUser=openid, t=123456, content = c, msgid = '98765433210' )
        with session_scope() as session:
            w = WeChatMsg(session, data)
            r = w.process()
            u = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            self.assertNotEqual(None, u)
            m = pickle.loads(u.sessionstr)
            self.assertTrue(m.has_key('menuid'))
            self.assertEqual(1, m['menuid'])
           
            d = XML(unicode(r).encode('utf-8'))
            xyz = WeChatTextMsgTest.Data()
            for x in d.iter():
                setattr(xyz, x.tag, x.text)
            for x in ('ToUserName', 'FromUserName', 'Content'):
                self.assertTrue(hasattr(xyz, x), x)
                
            self.assertEqual(touser, xyz.FromUserName, touser)
            self.assertEqual(openid, xyz.ToUserName, openid)
            self.assertEqual(xyz.Content, u'''欢迎进入收藏夹功能.
0:搜索
1:添加
2:删除
3:清空
[您当前位于功能：/收藏夹/]
(输入~可以返回根菜单， 输入../返回上一次菜单)''')
            
    
    def test_reenter(self):
        self.test_first()
        c = u'0'
        openid = '5678'
        touser = '1234'
        data = self.xmlstr.format(toUser=touser, fromUser=openid, t=123456, content = c, msgid = '98765433210' )
        with session_scope() as session:
            u1 = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            oldsessionstr = u1.sessionstr
            w = WeChatMsg(session, data)
            r = w.process()
            session.commit()
            #u1 will align with the database's data, no need query manually, the query will be triggered automatically
            self.assertNotEqual(u1.sessionstr, oldsessionstr)
            m = pickle.loads(u1.sessionstr)
            self.assertTrue(m.has_key('menuid'))
            self.assertEqual(2, m['menuid'])
            
    def test_invalidinput(self):
        self.test_first()
        c = u'好'
        openid = '5678'
        touser = '1234'
        data = self.xmlstr.format(toUser=touser, fromUser=openid, t=123456, content = c, msgid = '98765433210' )
        with session_scope() as session:
            u1 = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            w = WeChatMsg(session, data)
            r = w.process()
            session.commit()
            u2 = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            self.assertEqual(u1.sessionstr, u2.sessionstr)
            self.assertNotEqual(-1, r.find(u'''输入错误， 请重新输入
欢迎进入收藏夹功能.
0:搜索
1:添加
2:删除
3:清空
[您当前位于功能：/收藏夹/]
(输入~可以返回根菜单， 输入../返回上一次菜单)'''))

    def beforeSetup(self):
        #self.dbecho = True
        pass
suite = TestSuite()
for x in dir():
    x = eval(x)
    if isclass(x) and issubclass(x, testbase.BaseTestCase):
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(x))
                    
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)