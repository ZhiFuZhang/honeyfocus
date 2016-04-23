#-*- coding:utf-8 -*-
from sqlalchemy import Column, String, create_engine, Integer, Text
from sqlalchemy.orm import sessionmaker,deferred
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from helper import web_log
from tornado.options import options
import tornado
import time

Session = sessionmaker()
Base = declarative_base()

class SessionCounter(object):
    _created = 0
    _closed = 0

    @classmethod
    def on_create(cls):
        if cls.get_create_num() - cls.get_close_num() > 2000:
            warn = 'too many sessions are being running, exit create:%d, clsed:%d'
            web_log.error(warn%(cls.get_create_num(), cls.get_close_num()))
            tornado.ioloop.IOLoop.instance().stop()
        if  cls.get_create_num() - cls.get_close_num() > 200:
            warn = 'too many sessions are being running, please check. create:%d, clsed:%d'
            web_log.warn(warn%(cls.get_create_num(), cls.get_close_num()))
        if options.debug:
            info = 'db sessions create:%d, clsed:%d'
            web_log.debug(info%(cls.get_create_num(), cls.get_close_num()))


        cls._created = cls._created + 1
    @classmethod
    def get_create_num(cls):
        return cls._created
    
    @classmethod
    def on_close(cls):
        cls._closed = cls._closed + 1

    @classmethod
    def get_close_num(cls):
        return cls._closed


class User(Base):
    __tablename__ = 'usertable'
    uid = Column(Integer, primary_key = True)
    username = Column(String(50), index = True, unique = True)
    passwd = deferred(Column(String(64))) # passwd + salt, splited by ',', eg,  ABCD,EFG  ABCD is passwd, EFG is salt
    createtime = Column(Integer)
    logintime = Column(Integer, default = 0)
    failtimes = (Column(Integer, default = 0))
    updatetime = Column(Integer, default = 0)
    power = Column(Integer, default = 0)

class WeChatData(Base):
    __tablename__ = 'wechattable'
    appid = Column(String(32), primary_key = True)
    secret = deferred(Column(String(64)))
    token = deferred(Column(String(64)))
    access_token = deferred(Column(Text))
    expires_time = Column(Integer)
    iplist = deferred(Column(Text))

class SysConfig(Base):
    __tablename__ = "sysconfig"
    id = Column(Integer, primary_key = True)
    #if the rebootflag is changed , and then the webserver shall be exited
    # And then it will be started by some monitor tools such as supervisor
    rebootflag = Column(Integer, default=0) 
    

class BookMark(Base):
    __tablename__ = "bookmaark"
    id = Column(Integer, primary_key = True)
    openid = Column(Integer, index = True)
    content = Column(Text)
    
class UserSession(Base):
    __tablename__ = 'usersession'
    id = Column(Integer, primary_key = True)
    openid = Column(Integer, index = True)
    #dict struct
    sessionstr = Column(Text)
    createtime = Column(Integer)
    refreshtime = Column(Integer, index = True)

    @staticmethod
    def expire(refreshtime):
        t = time.time()
        #expire in 30 minutes
        if t > refreshtime + 1800:
            return True
        return False


def init(dbdrive, isEcho=True):
    engine = create_engine(dbdrive, echo=isEcho)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    SessionCounter.on_create()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        SessionCounter.on_close()
        session.close()
    