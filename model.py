from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

engine = create_engine("sqlite:///doglog.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

class DogWalker(Base):

    __tablename__ = "dogwalkers"
    id = Column(Integer, primary_key=True)
    user_email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)


    def __init__(self, user_email, password):
        self.user_email = user_email
        self.password = password
        
class  DogOwner(Base):

    __tablename__ = "dogowners"

    id = Column(Integer, primary_key=True)
    dog_owner_email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    dog_owner_name = Column(String(64), nullable=True)
    dog_owner_name = Column(Integer, nullable=True)
    emergency_name = Column(String(64), nullable=True)
    emergency_phone = Column(Integer, nullable=True)
    vet_name = Column(String(64), nullable=True)
    vet_phone = Column(Integer, nullable=True)
    dog_walker_id = Column(Integer, ForeignKey('dogwalkers.id'))

    dogwalker = relationship("DogWalker", backref=backref("dogwalkers", order_by=id))

class Dog(Base):

    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True)
    dog_owner_id = Column(Integer, ForeignKey('dogowners.id'))
    dog_name = Column(String(64), nullable=True)
    dog_breed = Column(String(64), nullable=True)
    dog_food = Column(String(64), nullable=True)
    dog_special_needs = Column(String(64), nullable=True)

    dog = relationship("DogOwner", backref=backref ("dogs", order_by=id))

class Event(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=False)
    location_lat = Column(Float(Precision=64), nullable=False)
    location_log = Column(Float(Precision=64), nullable=False)
    status = Column(Integer, nullable=True)
    notes = Column(String(64), nullable=False) 
    event_pic_url=Column(String(64),nullable=True)
    walk_id = Column(Integer, ForeignKey('walks.id'))
    dog_id = Column(Integer, ForeignKey('dogs.id'))

    walk = relationship("Walk", backref=backref ("events", order_by=id))
    dog = relationship("Dog", backref=backref ("events", order_by=id))

class Walk(Base):

    __tablename__ = "walks"

    id = Column(Integer, primary_key=True)
    dog_walker_id = Column(Integer, ForeignKey('dogwalkers.id'))
    obedience_rating = Column(Integer, nullable=False)
    dog_mood = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    walk_location=Column(Text, nullable=False)
    dogwalker = relationship("DogWalker", backref=backref ("walks", order_by=id))

class DogsOnWalk(Base):

    __tablename__ = "dogsonwalks"

    id = Column(Integer, primary_key=True)
    walk_id = Column(Integer, ForeignKey('walks.id'))
    dog_id = Column(Integer, ForeignKey('dogs.id'))  

    walk = relationship("Walk", backref=backref ("dogsonwalks", order_by=id))
    dog = relationship("Dog", backref=backref ("dogsonwalks", order_by=id))


def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()







