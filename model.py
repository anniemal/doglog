from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session
import os
# engine = create_engine('sqlite:///doglog.db', echo=True)
# engine = create_engine('postgres://nbnuegzevwjkmo:RQI2BlBCzwJC7IC7lWObacrwEi@ec2-23-21-176-133.compute-1.amazonaws.com:5432/d5d5pi8c5rbhue', echo=True)

# engine = create_engine('postgresql+psycopg2://kaboomboom:letterscleo@localhost:5432/doglog', echo=True)
db_uri = os.environ.get("DATABASE_URL", 'postgresql://kaboomboom:letterscleo@localhost:5432/doglog')
engine = create_engine(db_uri, echo = False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

class DogWalker(Base):

    __tablename__ = "dogwalkers"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64),nullable=False)
    last_name = Column(String(64),nullable=False)
    company_name = Column(String(64),nullable=True)
    phone_number = Column(Integer,nullable=False)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
        
class  DogOwner(Base):

    __tablename__ = "dogowners"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    phone_number=Column(Integer,nullable=False)
    email = Column(String(64), nullable=False)
    emergency_contact = Column(String(64), nullable=False)
    contact_phone = Column(Integer, nullable=False)
    vet_name = Column(String(64), nullable=False)
    vet_phone = Column(Integer, nullable=False)
    dogwalker_id = Column(Integer, ForeignKey('dogwalkers.id'))

    dogowner = relationship("DogWalker", backref=backref ("dogowners", order_by=id))

class Dog(Base):

    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('dogowners.id'))
    dog_name = Column(String(64), nullable=False)
    sex=Column(Integer, nullable=False)
    breed = Column(String(64), nullable=False)
    needs = Column(String(64), nullable=False)

    dog = relationship("DogOwner", backref=backref ("dogs", order_by=id))

# class Event(Base):

#     __tablename__ = "events"

#     id = Column(Integer, primary_key=True)
#     event_type = Column(String(64), nullable=False)
#     location_lat = Column(Float, nullable=False)
#     location_log = Column(Float, nullable=False)
#     status = Column(Integer, nullable=False)
#     notes = Column(String(64), nullable=False) 
#     event_pic_url = Column(String(64),nullable=True)
    # walk_id = Column(Integer, ForeignKey('walks.id'))
    # dog_id = Column(Integer, ForeignKey('dogs.id'))

    # walk = relationship("Walk", backref=backref ("events", order_by=id))
    # dog = relationship("Dog", backref=backref ("events", order_by=id))

class Walk(Base):

    __tablename__ = "walks"

    id = Column(Integer, primary_key=True)
    dog_walker_id = Column(Integer, ForeignKey('dogwalkers.id'))
    obedience_rating = Column(Integer, nullable=False)
    dog_mood = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    walk_location = Column(Text, nullable=False)
    elapsed_distance = Column(Float, nullable=False)
    elapsed_time = Column(String(64),nullable=False)
    events=Column(Text, nullable=True)
    walk_pic_url = Column(String(64),nullable=True)
    dogwalker = relationship("DogWalker", backref=backref ("walks", order_by=id))

# class DogsOnWalk(Base):

#     __tablename__ = "dogsonwalks"

#     id = Column(Integer, primary_key=True)
#     walk_id = Column(Integer, ForeignKey('walks.id'))
#     dog_id = Column(Integer, ForeignKey('dogs.id'))  
#     walk = relationship("Walk", backref=backref ("dogsonwalks", order_by=id))
#     dog = relationship("Dog", backref=backref ("dogsonwalks", order_by=id))
def create_db():
    Base.metadata.create_all(engine)

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()







