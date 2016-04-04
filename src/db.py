from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html

    
    
import sqlalchemy
from sqlalchemy import create_engine
print sqlalchemy.__version__ 
engine = create_engine('sqlite:///:memory:', echo=True)
#engine = create_engine('sqlite:///b.db', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence

class User(Base):
    __tablename__ = 'usertable'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(25), index = True, unique = True)
    fullname = Column(String)
    password = Column(String)
    def __repr__(self):
        return "<User(id='%d', name='%s', fullname='%s', password='%s')>" % (self.id, self.name, self.fullname, self.password)

#print  User.__table__
Base.metadata.create_all(engine)  
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
from sqlalchemy.orm import sessionmaker 
Session = sessionmaker(bind=engine)
session = Session()
session.add(ed_user) 
session.commit()
our_user = session.query(User).filter_by(name='ed').first()
print our_user
our_user.fullname = '99999'
session.commit()