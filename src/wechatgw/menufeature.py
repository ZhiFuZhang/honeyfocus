#-*- coding:utf-8 -*-
from db import session_scope, UserSession
import db
from string import strip
import pickle
import time
class BaseFeature(object):
    _InvalidNum = 237232167
    _InvalidTips = u'输入错误， 请重新输入\n'
    _SystemError = u'系统错误， 请稍后重试'
    def __init__(self, name, parent, root):
        #when user enter the parent level, output the name
        self.name = name
        self.parent = parent
        self.root = root
        if parent != self:
            self.pathname = parent.pathname +  self.name + '/'
        # i am the root
        if root == None or root == self:
            self.pathname = '/'
        self.objectid = self.root.createLink(self)   
        #need set a value in subclass
        self.sub = None
        # when user enter this level, output this tips
        self.tips = ''     
        
    def help(self):
        if hasattr(self, '_helpstr'):
            return self._helpstr
        else:
            i = 0
            s = self.tips + '\n'
            if self.sub:
                for a in self.sub:
                    s = s + str(i) +':' + a.name + '\n'
                    i = i + 1
                s = s + u'[您当前位于功能：'+ self.pathname+ ']' + '\n'
                s = s + self.shortcuststr()
            self._helpstr = s
            return self._helpstr
    

    def shortcuststr(self):
        return u'(输入~可以返回根菜单， 输入../返回上一次菜单)'
    
    def parentORroot(self, openid, content):
        if content == '~':
            return (self.root.objectid, self.root.help())
        elif content == '../':
            return (self.parent.objectid, self.parent.help())
        elif content == '?':
            return (self.objectid, self.help())
        return None
    
    def execute(self, openid, content):
        ret = self.parentORroot(openid, content)
        if ret:
            return ret
        #if this step is the last step, go to finalstep function
        if self.sub is None or len(self.sub) == 0:            
            return self.finalstep(openid, content)

        if content is None:
            return (self.objectid, self.help())
        
        i = self._InvalidNum
        
        if content.isdigit():
            i = int(content)
        if i < len(self.sub):
            return self.sub[i].execute(openid, None)
        else:
            return (self.objectid, self._InvalidTips + self.help())
        
    def finalstep(self, openid, content):
        return (self.objectid, self.help())
        
class RootFeature(BaseFeature):
    def __init__(self):
        self.featurelist = []
        super(RootFeature, self).__init__('root', self, self)
        self.tips = u'您好， 欢迎来到心中的日月， 请选择功能'
        self.sub = [BookMarkFeature(self, self.root),
                    VersionFeature(self, self.root)
                    ]
    def createLink(self, obj):
        i = 0
        for x in self.featurelist:
            if x == obj:
                return i
            i = i + 1
        self.featurelist.append(obj)
        return len(self.featurelist) - 1
    
    def execute(self, openid, content):
        if not content or not content.isdigit():
            return (self.objectid, self.help())
    
        return BaseFeature.execute(self, openid, content)

    def getFfeature(self, objectid):
        if objectid >= len(self.featurelist):
            return None
        return self.featurelist[objectid]

class VersionFeature(BaseFeature):
    def __init__(self, parent, root):
        super(VersionFeature, self).__init__(u'关于honeyfocus', parent, root)
        self.tips = ''
    def finalstep(self, openid, content):
        return (self.parent.objectid, u'''联系人:zzfooo@hotmail.com''')
class BookMarkFeature(BaseFeature):
    Name = u'收藏夹'
    def __init__(self, parent, root):
        super(BookMarkFeature, self).__init__(self.Name, parent, root)
        self.tips = u'欢迎进入收藏夹功能.'
        self.sub = [BookMarkFeature.SearchAction(self, self.root),
                    BookMarkFeature.AddAction(self, self.root),
                    BookMarkFeature.DeleteAction(self, self.root),
                    BookMarkFeature.ClearAction(self, self.root),
                    ]

    #sub class
    class AddAction(BaseFeature):
        Name = u'添加'
        def __init__(self, parent, root):
            super(BookMarkFeature.AddAction, self).__init__(self.Name, parent, root)
            self.tips = u'请输入想收藏的内容'
            
        def finalstep(self, openid, content):
            if content is None:
                return (self.objectid, self.help())
            content = strip(content)
            ret = u''
            with session_scope() as session:
                a = db.BookMark(content=content)
                session.add(a)
                session.commit()
                ret = u'添加成功, 标示为:#'+ str(a.id)
            return (self.objectid, ret)

        
    class SearchAction(BaseFeature):
        Name = u'搜索'
        PageNum = 7
        def __init__(self, parent, root):
            super(BookMarkFeature.SearchAction, self).__init__(self.Name, parent, root)
            self.tips = u'请输入想收藏的内容'
        
        def _saveArgs(self,session,openid, page, querystr):
            u = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            if u and u.sessionstr:
                m = pickle.loads(u.sessionstr)    
                m['page']  = page
                m['querystr'] = querystr

                u.sessionstr = pickle.dumps(m)
                u.refreshtime = int(time.time())
            else:
                u = UserSession()
                u.createtime = int(time.time())
                m = dict()
                m['page']  = page
                m['querystr'] = querystr
                u.openid = openid
                u.sessionstr = pickle.dumps(m)
                u.refreshtime = int(time.time())
                session.add(u)
                
        def _clearArgs(self, session, openid):
            u = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            if u and u.sessionstr:
                m = pickle.loads(u.sessionstr)
                if m.has_key('page'):
                    m.pop('page')
                if m.has_key('querystr'):
                    m.pop('querystr')
                u.sessionstr = pickle.dumps(m)
            
        
        def _restoreArgs(self, session,openid):
            u = session.query(UserSession).filter(UserSession.openid == openid).one_or_none()
            if u and u.sessionstr:
                if u.expire(u.refreshtime):
                    u.sessionstr = ''
                    return None
                
                m = pickle.loads(u.sessionstr) 
                if m.has_key('page') and m.has_key('querystr'):
                    return (m['page'], m['querystr'])
                return None    
            else:
                return None

        def parentORroot(self, openid, content):
            ret = BaseFeature.parentORroot(self, openid, content)
            if ret:
                with session_scope() as session:
                    self._clearArgs(session, openid)
            return ret
        
        def finalstep(self, openid, content):
            if content is None:
                return (self.objectid, self.help())
            
            content = strip(content)
            
            if len(content) == 0:
                return (self.objectid, u'')
            ret = u''
        
            with session_scope() as session:
                page = 0
                if content == '.':
                    args = self._restoreArgs(session,openid)
                    if args:
                        page, content = args
                        page = page + 1
                    #if no record, consider '.' as a user input
                    
                # each page we will display 8 items, 
                #but the last item in the page will be displayed as the first item in the next page
                start = page *self.PageNum
                stop = start + self.PageNum + 1
                s = content.replace('%', r'\%')
                result = session.query(db.BookMark).filter(db.BookMark.openid == openid)
                result = result.filter(db.BookMark.content.like('%' + s + '%', escape= '\\')).slice(start, stop)
                total = 0
                for row in result:
                    ret = ret + '#' + str(row.id) + '.' + row.content + '\n'
                    total = total + 1
                if total == 0:
                    ret = u'没有找到关键字<' + content + u'>相关的内容'
                else:
                    ret = '<' + content + u'>搜索结果如下：\n' + ret
                if total > self.PageNum:
                    self._saveArgs(session, openid, page, content)
                    ret = ret  + u'{请输入  。 查看下一页的搜索结果, 或者输入其它关键字重新搜索}'
                else:
                    self._clearArgs(session, openid)
                
            return (self.objectid, ret)
            
    class DeleteAction(BaseFeature):
        Name = u'删除'
        def __init__(self, parent, root):
            super(BookMarkFeature.DeleteAction, self).__init__(self.Name, parent, root)
            self.tips = u'请输入删除的id'
        def finalstep(self, openid, content):
            if content is None:
                return (self.objectid, self.help())
                        
            content = strip(content)
            if len(content) < 2 or content[0] != '#':
                return (self.objectid, u'输入非法， 请重新输入')
            
            content = content[1:len(content)]
            ret = u'<%s>删除成功'%content
            with session_scope() as session:            
                c = session.query(db.BookMark).filter(db.BookMark.id == content).delete(synchronize_session = False);
                if not c:
                    ret = u'没有<%s>相关记录'%content
            return (self.objectid, ret)


    class ClearAction(BaseFeature):
        Name = u'清空'
        def __init__(self, parent, root):
            super(BookMarkFeature.ClearAction, self).__init__(self.Name, parent, root)
            self.tips = u'请输入9确认, 输入其它任何字符取消'
        def finalstep(self, openid, content):
            # need a confirm
            if content is None:
                return (self.objectid, self.tips)
            if strip(content) == '9':
                with session_scope() as session:
                    session.query(db.BookMark).filter(db.BookMark.openid == openid).delete(synchronize_session = False)
                ret = u'清楚完成'
                return (self.parent.objectid, ret)
            else:
                return (self.parent.objectid, self.parent.helo())
            
            return (self.parent.objectid, self.parent.helo())


rootFeature = RootFeature()