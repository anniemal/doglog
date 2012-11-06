from dateutil import parser
import model
import csv
import time

def load_users(session):
    with open('seed_data/u.user') as csvfile:
        user_raw_data=csv.reader(csvfile, delimiter='|')
        for row in user_raw_data:

            #Each row is a list of user data
            #Create a User object for each row and put it into database
            age = row[1]
            zipcode = row[4]
            email = None
            password = None

            new_user = model.User(age, zipcode, email, password)
            session.add(new_user)
            session.commit()

def load_movies(session):
    with open('seed_data/u.item') as csvfile:
        movie_raw_data= csv.reader(csvfile, delimiter='|')
        for row in movie_raw_data:
            movie_title=row[1]
            release_date=row[2]
            IMDB_url=row[4]
            formatted_date=parser.parse(release_date)
            


            new_movie=model.Movie(movie_title.decode("latin_1"),formatted_date,IMDB_url)
            print new_movie
            session.add(new_movie)
            session.commit()


def load_ratings(session):
    with open('seed_data/u.data') as csvfile:
        ratings_raw_data = csv.reader(csvfile, dialect="excel-tab")
        for row in ratings_raw_data:
            user_id = row[0]
            movie_id = row[1]
            rating = row[2]

            new_rating = model.Rating(user_id, movie_id, rating)
            session.add(new_rating)
            session.commit()

def main(session):
    """We already ran these and seeded our database"""
    #load_users(session)
    #load_movies(session)
    #load_ratings(session)   ##This takes a very long time to run. So don't run it.

if __name__ == "__main__":
    s= model.connect()
    main(s)