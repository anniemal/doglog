from flask import Flask, render_template, redirect, request, session, flash, jsonify
import model
import sqlalchemy
import json
import datetime
from sqlalchemy import DateTime
import time
from datetime import datetime

app = Flask(__name__)

SECRET_KEY = 'power_pose'
app.config.from_object(__name__)

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
    try:
        email = request.form['email']
        password = request.form['password']
        ## Check to see if user is a dogwalker
        logged_in_user=model.session.query(model.DogWalker).select((DogWalker.email==email) & (DogWalker.password==password))
        if logged_in_user:
            session['user_id']=logged_in_user.id
            return redirect ("/dogwalker")
    except: 
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
    ## Check to see if user is a dogwalker    
    results = model.session.query(model.DogWalker).filter(model.DogWalker.email==email).filter(model.DogWalker.password==password).all()
    if len(results) == 1:
        logged_in_user=results[0]
        print logged_in_user
        if logged_in_user:
            logged_in_user_id=jsonify(user_id=logged_in_user.id)
            print logged_in_user_id
            return logged_in_user_id
    else:
        return jsonify(error="Sorry, wrong email/password. Please try logging in or create a new account.")
         
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
    walk_location=str(walk_location)
    print walk_location
    new_walk=model.Walk(dog_walker_id=dog_walker_id,obedience_rating=obedience_rating,dog_mood=dog_mood,start_time=start_time, \
        end_time=end_time,walk_location=walk_location)
    model.session.add(new_walk)
    model.session.commit()
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
    # user_id=session['user_id']
    # user=model.session.query(model.DogWalker).get(user_id)
    # owners=model.session.query(model.DogOwner).filter_by(dogwalker_id=user_id).all()
    # owners_id=[]
    # for owner in owners:
    #     owners_id.append(owner.id)
    # print owners_id
    # dogs={}
    # for owner in owners_id:
    #     dogs[owner]=model.session.query(model.Dog).filter_by(owner_id=owner).all()
    # print dogs
    # return render_template("log_log.html",first_name=user.first_name,owners_id=owners_id,dogs=dogs,owners=owners)
    tup=get_sidebar()
    return render_template("log_log.html",first_name=tup[0],owners_id=tup[1],dogs=tup[2],owners=tup[3],user_id=tup[4])
@app.route("/save_dogs")
def save_dogs():
    return render_template("log_dog.html")

if __name__ == "__main__":
    app.run('0.0.0.0', debug = True)