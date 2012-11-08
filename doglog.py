from flask import Flask, render_template, redirect, request, session, flash
import model
from skaffold import Skaffold

app = Flask(__name__)

SECRET_KEY = 'power_pose'
app.config.from_object(__name__)

# Skaffold(app, model.DogWalker, session)
# Skaffold(app, model.DogOwner, session)
# Skaffold(app, model.Dog, session)
# Skaffold(app, model.Event, session)-
# Skaffold(app, model.Walk, session)
# Skaffold(app, model.DogsOnWalk, session)

@app.route("/")
def index():
    error=""
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
        logged_in_user=model.session.query(model.DogOwner).select((DogOwner.email==email) & (DogOwner.password==password))
        if logged_in_user:    
            session['user_id']=logged_in_user.id
            return redirect ("/dogowner")
    except: 
        error="Sorry, wrong email address/password. Please re-try logging in, or create a new account."
        return render_template("/index.html", error=error)  

@app.route("/user_reg", methods=["GET","POST"])
def user_reg():
    return render_template("user_reg.html")

@app.route("/dogowners_reg", methods=["GET","POST"])
def dogowners_reg():
    return render_template("dogowners_reg.html")

@app.route("/save_user", methods=["GET","POST"])
def save_user():
    print "here"
    first_name=request.form['input_first_name']

    last_name=request.form['input_last_name']
    company_name=request.form['input_company_name']
    phone_number=request.form['input_phone']
    email=request.form['input_email']
    password=request.form['input_password']

 
    # emergency_contact=request.form['input_emergency_contact']
    # contact_number=request.form['input_contact_phone']
    # vet_name=request.form['input_vet_name']
    # vet_phone=request.form['input_vet_phone']
    # dog_walker_email=request.form['input_email_dog_walker']
    # dog_name=request.form['input_dog_name']
    # sex=request.form['input_sex']
    # breed=request.form['input_breed']
    # needs=request.form['input_needs']

    new_user=model.DogWalker(first_name=first_name,last_name=last_name,company_name=company_name,phone_number=phone_number,email=email,password=password)
    model.session.add(new_user)
    model.session.commit()
    return redirect("/add_owner")
    
@app.route("/add_owner")
def add_owner():

    return render_template("add_owner.html")

@app.route("/save_owner")
def save_owner():
    # DogOwner Table information
    print "1"
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    print "2"
    phone_number=request.form['phone_number']
    email=request.form['email']
    emergency_contact=request.form['emergency_contact']
    contact_number=request.form['contact_phone']
    vet_name=request.form['vet_name']
    vet_phone=request.form['vet_phone']
    #Dog Table information
    print "3"
    dog_name=request.form['dog_name']
    sex=request.form['sex']
    breed=request.form['breed']
    needs=request.form['needs']
    print "te"
    new_owner=model.DogOwner(first_name=first_name,last_name=last_name,phone_number=phone_number,email=email, emergency_contact=emergency_contact,\
        contact_number=contact_number,vet_name=vet_name,vet_phone=vet_phone)
    model.session.add(new_owner)
    model.session.commit()
    print "here"
    new_dog=model.Dog(owner_id=new_owner.id,dog_name=dog_name,sex=sex,breed=breed,needs=needs)
    model.session.add(new_dog)
    model.session.commit()
    print "there"

    return render_template("log_log.html")

@app.route("/save_dogs")
def save_dogs():
    return render_template("log_dog.html")

if __name__ == "__main__":
    app.run(debug = True)