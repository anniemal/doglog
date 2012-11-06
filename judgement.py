from flask import Flask, render_template, redirect, request, session, flash
import model

app = Flask(__name__)

SECRET_KEY = 'power_pose'
app.config.from_object(__name__)

@app.route("/")
def index():
    user_list=model.session.query(model.User).all()
    return render_template("user_list.html", users = user_list)

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
        id_entered = request.form['id']
        logged_in_user=model.session.query(model.User).filter_by(id=id_entered).one()
        if logged_in_user:
            session['user_id']=id_entered
            return redirect ("/user_ratings")
    except: 
        flash("Invalid user id")
        return redirect("/login")    


if __name__ == "__main__":
    app.run(debug = True)