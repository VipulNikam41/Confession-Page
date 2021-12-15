from flask import Flask, render_template, request, redirect, session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy.orm.util import identity_key

# libraries to handle database

from datetime import datetime

from multiprocessing import Process
import time
# libraries to handle multiprocessing while program sleeps for 10 sec.

app = Flask(__name__)
app.secret_key = "Vipul"

# initialize SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///confession.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

app.config['SQLALCHEMY_BINDS'] = {
    "userName" : "sqlite:///users.db"
}

app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)

class dataBase(db.Model):
	# creating dataBase with four columns
    sno = db.Column(db.Integer, primary_key=True) #unique_identifier
    name = db.Column(db.String(10), nullable=False) #first Number
    text = db.Column(db.String(200), nullable=False) #first Number
    tags = db.Column(db.String(30)) #first Number
    date = db.Column(db.DateTime, default = datetime.utcnow) #to store answers

    # Constructor
    def __init__(self, name, text, tags):
        self.name = name
        self.text = text
        self.tags = tags

    #to get class object in the form of string for /show api call
    def __repr__(self) -> str:
        return f"{self.sno}\t{self.name}\t{self.text}\t{self.tags}\t{self.date}\n"

class userName(db.Model):
    __bind_key__ = "userName"
	# creating dataBase with four columns
    name = db.Column(db.String(10), primary_key=True) #first Number
    password = db.Column(db.String(200), nullable=False) #first Number

    # Constructor
    def __init__(self, name, password):
        self.name = name
        self.password = password

    #to get class object in the form of string for /show api call
    def __repr__(self) -> str:
        return f"{self.name}\t{self.password}\n"


# Home Page
@app.route("/")
def index():
	# By default Status code will be 200
    return render_template('index.html', name = "")

@app.route("/addConfession")
def addConf():
    if "user" in session:
        Uname = session["user"]
        return render_template('addConf.html', name = Uname)

    return f"you are not logged in, please log in and try again"

@app.route("/massege", methods = ['GET', 'POST'])
def massege():
    if "user" in session:
        Uname = session["user"]
        conf = request.form['conf']
        tags = request.form['tag']

        post = dataBase(name = Uname, text = conf, tags = tags)
        db.session.add(post)
        db.session.commit()
        return "confession added successfully"

    return f"you are not logged in, please log in and try again"

@app.route("/myConfession")
def myConf():
    if "user" in session:
        Uname = session["user"]
        allPost = []
        for row in db.session.query(dataBase):
            if Uname == row.name:
                allPost.append(row)
        return render_template('myConf.html', allPost = allPost, name = Uname)

    return f"you are not logged in, please log in and try again"

@app.route("/edit", methods = ['GET', 'POST'])
def editConf():
    if "user" in session:
        Uname = session["user"]
        key = request.form.get("sno")
        # print(key)
        instance = dataBase.query.get_or_404(key)
        # print(instance)
        return render_template('editconf.html', name = Uname, txt = instance.text, tgs = instance.tags, key = key)

    return f"you are not logged in, please log in and try again"

@app.route("/update", methods = ['GET', 'POST'])
def update():
    if "user" in session:
        Uname = session["user"]
        newText = request.form['conf']
        newTags = request.form['tag']
        key = request.form.get("sno")
        # print(key)
        instance = dataBase.query.get_or_404(key)
        instance.text = newText
        instance.tags = newTags
        db.session.commit()
        # print(instance)
        return render_template('myConf.html', name = Uname, txt = instance.text, tgs = instance.tags)

    return f"you are not logged in, please log in and try again"

@app.route("/delete", methods = ['GET', 'POST'])
def deletConf():
    if "user" in session:
        Uname = session["user"]
        # key = request.form['sno']
        key = request.form.get("sno")
        print(key)
        dataBase.query.filter_by(sno=key).delete()
        db.session.commit()

        allPost = []
        for row in db.session.query(dataBase):
            if Uname in row.name:
                allPost.append(row)
        return render_template('myConf.html', allPost = allPost, name = Uname)
    return f"you are not logged in, please log in and try again"

# to add numbers in database from url
@app.route("/search/word/<string:key>")
def SearchWord(key):
    if "user" not in session:
        return f"you are not logged in, please log in and try again"
    # print(key)
    # key = " " + key + " "
    allPost = []
    for row in db.session.query(dataBase):
        if key in row.text:
        	allPost.append(row)
    return render_template('display.html', allPost = allPost, name = session["user"])

@app.route("/search/tag/<string:key>")
def SearchTag(key):
    if "user" not in session:
        return f"you are not logged in, please log in and try again"
    # print(key)
    # key = " " + key + " "
    allPost = []
    for row in db.session.query(dataBase):
        if key in row.tags:
        	allPost.append(row)
    return render_template('display.html', allPost = allPost, name = session["user"])

@app.route("/search/<string:date1>/<string:date2>")
def Filterdate(date1,date2):
    if "user" not in session:
        return f"you are not logged in, please log in and try again"
    qry = dataBase.query.filter( dataBase.date.between(date1, date2) )
    # print(qry)

    msg = f"confessions posted between {date1} and {date2} are: "

    allPost = []
    for row in qry:
        allPost.append(row)

    return render_template('display.html', mag = msg, allPost = allPost, name = session["user"])

@app.route("/url", methods = ['GET', 'POST'])
def Urldate():
    date1 = request.form['date1']
    date2 = request.form['date2']
    if date2 == "":
        date2 = datetime.utcnow
    link = f"/search/{date1}/{date2}"
    print(link)
    return redirect(link)

@app.route("/word", methods = ['GET', 'POST'])
def Urlword():
    word = request.form['word']
    link = f"/search/word/{word}"
    print(link)
    return redirect(link)

@app.route("/tag", methods = ['GET', 'POST'])
def Urltag():
    tag = request.form['tag']
    link = f"/search/tag/{tag}"
    print(link)
    return redirect(link)

@app.route("/show", methods = ['GET', 'POST'])
def show():
    # to show database in browser
    if request.method == "POST":
        Uname = request.form['Uname']
        password = request.form['password']
        ex = db.session.query(exists().where(userName.name == Uname)).scalar()
        if ex == False:
            usr = userName(Uname, password)
            db.session.add(usr)
            db.session.commit()
            return render_template('add.html')
        # getting the row beloning to given instance
        instance = userName.query.get_or_404(Uname)
        if instance.password == password:
            session["user"] = Uname
            allPost = []
            for row in db.session.query(dataBase):
                allPost.append(row)
            return render_template('display.html', allPost = allPost, name = Uname)
        else:
            return render_template('wrong.html')    
    elif "user" in session:
        Uname = session["user"]
        allPost = []
        for row in db.session.query(dataBase):
            allPost.append(row)
        return render_template('display.html', allPost = allPost, name = Uname)

    return f"you are not logged in, please log in and try again"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template('index.html')

if __name__ == "__main__":
	# main function
    app.run(debug=True, port=5000)