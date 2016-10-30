from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime

engine = create_engine('sqlite:///:memory:')

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # columns
    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)

    def __repr__(self):
        return "<User(firstname='{}', lastname='{}')>".format(self.firstname, self.lastname)

