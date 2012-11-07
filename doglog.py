from flask import Flask, render_template, redirect, request, session, flash
import model
from skaffold import Skaffold


app = Flask(__name__)

SECRET_KEY = 'power_pose'
app.config.from_object(__name__)


# Skaffold(app, model.DogWalker, session)
# Skaffold(app, model.DogOwner, session)
# Skaffold(app, model.Dog, session)
# Skaffold(app, model.Event, session)
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
        logged_in_user=model.session.query(model.DogWalker).select((DogWalker.user_email==email) & (DogWalker.password==password))
        if logged_in_user:
            session['user_id']=logged_in_user.id
            return redirect ("/dogwalker")
        logged_in_user=model.session.query(model.DogOwner).select((DogOwner.Useremail==email) & (DogOwner.password==password))
        if logged_in_user:    
            session['user_id']=logged_in_user.id
            return redirect ("/dogowner")
    except: 
        error="Sorry, wrong email address/password. Please re-try logging in, or create a new account."
        return render_template("/index.html", error=error)  

@app.route("/dogwalkers_reg", methods=["GET","POST"])
def dogwalkers_reg():
    return render_template("dogwalkers_reg.html")

@app.route("/dogowners_reg", methods=["GET","POST"])
def dogowners_reg():
    return render_template("dogowners_reg.html")

if __name__ == "__main__":
    app.run(debug = True)