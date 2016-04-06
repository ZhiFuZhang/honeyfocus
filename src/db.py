#-*- coding:utf-8 -*-
from sqlalchemy import Column, String, create_engine, Integer, Text
from sqlalchemy.orm import sessionmaker,deferred
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager


Session = sessionmaker()
Base = declarative_base()

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

class sysconfig(Base):
    __tablename__ = "sysconfig"
    id = Column(Integer, primary_key = True)
    #if the rebootflag is changed , and then the webserver shall be exited
    # And then it will be started by some monitor tools such as supervisor
    rebootflag = Column(Integer, default=0) 
    




def init(dbdrive, isEcho=True):
    engine = create_engine(dbdrive, echo=True)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    
