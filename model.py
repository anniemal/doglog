from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):

    __tablename__="Users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=True)
    zipcode = Column(String(15), nullable=True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable=True)

    def __init__(self, age, zipcode, email=None, password=None):
        self.age = age
        self.zipcode = zipcode
        self.email = email
        self.password = password


class Movie(Base):

    __tablename__="Movies"

    id=Column(Integer, primary_key=True)
    movie_title=Column(String(64), nullable=False)
    release_date= Column(DateTime, nullable=False)
    IMDB_url=Column(String(64), nullable=True)

    def __init__(self,movie_title, release_date, IMDB_url=None):
        self.movie_title= movie_title
        self.release_date=release_date
        self.IMDB_url=IMDB_url

class Rating(Base):

    __tablename__ = "Ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    movie_id = Column(Integer, ForeignKey('Movies.id'))
    rating = Column(Integer)

    #define these attributes, linked from another table
    user = relationship ("User", backref=backref("ratings", order_by=id))
    movie = relationship("Movie", backref=backref("ratings", order_by=id))

    def __init__(self, user_id, movie_id, rating):
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating


### End class declarations

def connect():
    """We moved this outside the function to the top"""
    # global ENGINE
    # global Session

    # ENGINE = create_engine("sqlite:///ratings.db", echo=True)
    # Session = sessionmaker(bind=ENGINE)

    # return Session()
    pass


def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()







