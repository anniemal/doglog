import os
from twilio.rest import TwilioRestClient
from flask import Flask, render_template, redirect, request, session, flash, jsonify
import model
import sqlalchemy
import json
import datetime
from sqlalchemy import DateTime
import time
from datetime import datetime
import string
from flask.ext.sqlalchemy import SQLAlchemy

SECRET_KEY = 'power_pose'

app = Flask(__name__)
app.config.from_object(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# db=SQLAlchemy(app)

@app.route("/")
def index():
    error = ""
    return render_template("index.html", error=error)

@app.route("/login", methods=["GET","POST"])
def login():
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session['user_id'] = None
    return redirect("/login")

@app.route("/authenticate", methods=["GET","POST"])
def authenticate():
        email = request.form['email']
        password = request.form['password']
        ## Check to see if user is a dogwalker
        results = model.session.query(model.DogWalker).filter(model.DogWalker.email==email).filter(model.DogWalker.password==password).all()
        if len(results) == 1:
            logged_in_user=results[0]
            print logged_in_user
            if logged_in_user:
                session['user_id']=logged_in_user.id
                return redirect ("/log")
        else:
            error="Sorry, wrong email address/password. Please re-try logging in, or create a new account."
            return render_template("/index.html", error=error)  

@app.route("/m_authenticate", methods=["GET","POST"])
def m_authenticate():
    print "here"
    print request.form
    email = request.form['email']
    password = request.form['password']
    print email
    print password
   
    results = model.session.query(model.DogWalker).filter(model.DogWalker.email==email).filter(model.DogWalker.password==password).all()
    if len(results) == 1:
        logged_in_user=results[0]
        print logged_in_user
        if logged_in_user:
            logged_in_user_id=jsonify(user_id=logged_in_user.id)
            print logged_in_user_id
            return logged_in_user_id
    else:
        return jsonify(user_id="error")
         
@app.route("/user_reg", methods=["GET","POST"])
def user_reg():
    return render_template("user_reg.html")

@app.route("/dogowners_reg", methods=["GET","POST"])
def dogowners_reg():
    return render_template("dogowners_reg.html")

@app.route("/save_user", methods=["GET","POST"])
def save_user():

    first_name=request.form['input_first_name']
    last_name=request.form['input_last_name']
    company_name=request.form['input_company_name']
    phone_number=request.form['input_phone']
    email=request.form['input_email']
    password=request.form['input_password']
    print email
    print password
    new_user=model.DogWalker(first_name=first_name,last_name=last_name,company_name=company_name,phone_number=phone_number,email=email,password=password)
    model.session.add(new_user)
    model.session.commit()
    session['user_id']=new_user.id
    return redirect("/add_owner")

@app.route("/m_save_user", methods=["GET","POST"])
def m_save_user():

    first_name=request.form['first_name']
    last_name=request.form['last_name']
    company_name=request.form['company_name']
    phone_number=request.form['phone']
    email=request.form['email']
    password=request.form['password']
    print email
    print password
    new_user=model.DogWalker(first_name=first_name,last_name=last_name,company_name=company_name,phone_number=phone_number,email=email,password=password)
    model.session.add(new_user)
    model.session.commit()
    new_user_id=jsonify(user_id=new_user.id)
    return new_user_id

@app.route("/m_save_map", methods=["GET", "POST"])
def m_save_map():   
    string_json=request.form['json_vals']
    json_obj=json.loads(string_json)
    dog_walker_id=json_obj['dogwalker_id']
    print dog_walker_id
    obedience_rating=json_obj['obedience_rating']
    print obedience_rating
    dog_mood=json_obj['dog_mood']
    print dog_mood
    start_time=json_obj['start_time']
    start_time = datetime.strptime(start_time[0:19],"%Y-%m-%dT%H:%M:%S")
    print start_time
    end_time=json_obj['end_time']
    print end_time
    end_time =datetime.strptime(end_time[0:19],"%Y-%m-%dT%H:%M:%S")
    walk_location=json_obj['walk_location']
    walk_location=json.dumps(walk_location)
    elapsed_distance = json_obj['elapsed_distance']
    print elapsed_distance 
    elapsed_time = json_obj['elapsed_time']
    event_data=json_obj['events']
    event_data=json.dumps(event_data)
    walk_pic_url=json_obj['walk_pic_url']
    print event_data
    print elapsed_time
    print walk_location
    walk_pic_url='kjsdf'
    new_walk=model.Walk(dog_walker_id=dog_walker_id,obedience_rating=obedience_rating,dog_mood=dog_mood,start_time=start_time, \
        end_time=end_time,walk_location=walk_location,elapsed_distance=elapsed_distance,elapsed_time=elapsed_time, events=event_data, walk_pic_url=walk_pic_url)
    model.session.add(new_walk)
    model.session.commit()

    owner=model.session.query(model.DogOwner).filter_by(dogwalker_id=dog_walker_id).one()
    dog=model.session.query(model.Dog).filter_by(owner_id=owner.id).one()
    account = "AC7225c1d30d2cce103ea56289e3fc6ed8"
    token = "6efbc4e502a9672e69fddf93c981cbbe"
    client = TwilioRestClient(account, token)

    message = client.sms.messages.create(to="+15625474270", from_="+14155994769",\
                                     body="%s wants to tell you that she walked for %d miles for %s time.") %(dog.name,
                                     elapsed_distance, elapsed_time)



    return "success"

@app.route("/add_owner",methods=["GET","POST"])
def add_owner():

    return render_template("add_owner.html")

@app.route("/dog_info/<int:owner_id>/<int:dog_id>",methods=["GET","POST"])
def dog_info(owner_id,dog_id):

    tup=get_sidebar()
    dog=model.session.query(model.Dog).filter_by(id=dog_id).one()
    dogowner=model.session.query(model.DogOwner).filter_by(id=owner_id).one()

    return render_template("dog_info.html",first_name=tup[0],owners_id=tup[1],dogs=tup[2],owners=tup[3],dog=dog,dogowner=dogowner )

@app.route("/save_owner",methods=["GET","POST"])
def save_owner():
    # DogOwner Table information
   
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    
    phone_number=request.form['phone_number']
    email=request.form['email']
    emergency_contact=request.form['emergency_contact']
    contact_phone=request.form['contact_phone']
    vet_name=request.form['vet_name']
    vet_phone=request.form['vet_phone']
    #Dog Table information
   
    dog_name=request.form['dog_name']
    sex=request.form['sex']
    breed=request.form['breed']
    needs=request.form['needs']
  
    new_owner=model.DogOwner(first_name=first_name,last_name=last_name,phone_number=phone_number,email=email, emergency_contact=emergency_contact,\
        contact_phone=contact_phone,vet_name=vet_name,vet_phone=vet_phone, dogwalker_id=session['user_id'])
    model.session.add(new_owner)
    model.session.commit()
    
    new_dog=model.Dog(owner_id=new_owner.id,dog_name=dog_name,sex=sex,breed=breed,needs=needs)
    model.session.add(new_dog)
    model.session.commit()

    return redirect("/log")

def get_sidebar():
    user_id=session['user_id']
    user=model.session.query(model.DogWalker).get(user_id)
    owners=model.session.query(model.DogOwner).filter_by(dogwalker_id=user_id).all()
    owners_id=[]
    for owner in owners:
        owners_id.append(owner.id)
    print owners_id
    dogs={}
    for owner in owners_id:
        dogs[owner]=model.session.query(model.Dog).filter_by(owner_id=owner).all()
    tup=(user.first_name,owners_id,dogs,owners,user.id)
    return tup

@app.route("/log")
def log():
    tup=get_sidebar()
    walks=model.session.query(model.Walk).filter_by(dog_walker_id=tup[4]).all()
    walk=model.session.query(model.Walk).filter_by(dog_walker_id=tup[4]).first()
    walk_as_dict = { 
        'walk_id': walk.id, \
        'dog_walker_id' : walk.dog_walker_id, \
        'obedience_rating' : walk.obedience_rating, \
        'dog_mood' : walk.dog_mood, \
        'start_time' : str(walk.start_time), \
        'end_time' : str(walk.end_time), \
        'walk_location' : walk.walk_location, \
        'elapsed_distance' :walk.elapsed_distance, \
        'elapsed_time' : walk.elapsed_time, \
        'events' : walk.events, \
        'walk_pic_url' : walk.walk_pic_url}

    json_walks=json.dumps(walk_as_dict)
    return render_template("log_log.html",first_name=tup[0],owners_id=tup[1],dogs=tup[2],owners=tup[3],\
        user_id=tup[4], json_walks=json_walks, elapsed_time=walk_as_dict['elapsed_time'], obedience_rating=walk_as_dict['obedience_rating'], \
        dog_mood=walk_as_dict['dog_mood'], elapsed_distance=walk_as_dict['elapsed_distance'], walk_pic_url=walk_as_dict['walk_pic_url'], walks=walks,\
        start_time=walk_as_dict['start_time'])

@app.route("/past_log/<int:walk_id>",methods=["GET","POST"])
def past_log(walk_id):

    tup=get_sidebar()
    walks=model.session.query(model.Walk).filter_by(dog_walker_id=tup[4]).all()
    walk=model.session.query(model.Walk).filter_by(id=walk_id).one()
    walk_as_dict = { 
        'walk_id': walk.id, \
        'dog_walker_id' : walk.dog_walker_id, \
        'obedience_rating' : walk.obedience_rating, \
        'dog_mood' : walk.dog_mood, \
        'start_time' : str(walk.start_time), \
        'end_time' : str(walk.end_time), \
        'walk_location' : walk.walk_location, \
        'elapsed_distance' :walk.elapsed_distance, \
        'elapsed_time' : walk.elapsed_time, \
        'events' : walk.events, \
        'walk_pic_url' : walk.walk_pic_url}

    json_walks=json.dumps(walk_as_dict)
    return render_template("log_log.html",first_name=tup[0],owners_id=tup[1],dogs=tup[2],owners=tup[3],\
        user_id=tup[4], json_walks=json_walks, elapsed_time=walk_as_dict['elapsed_time'], obedience_rating=walk_as_dict['obedience_rating'], \
        dog_mood=walk_as_dict['dog_mood'], elapsed_distance=walk_as_dict['elapsed_distance'], walk_pic_url=walk_as_dict['walk_pic_url'], walks=walks,\
        start_time=walk_as_dict['start_time'])

@app.route("/save_dogs")
def save_dogs():
    return render_template("log_dog.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)