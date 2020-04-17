from flask import Flask,render_template
from flask import Flask, flash, request, redirect, render_template, make_response
import urllib.request
import requests   
import os
import pickle
import json
import codecs
from flask import send_from_directory
from flask_cors import CORS
from functools import wraps
from os import path


app = Flask(__name__)
cors = CORS(app)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt','json','zip'])

users = []
credentials = {}

def support_jsonp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route("/") 
def home():
    return render_template("login.html")

@app.route("/register") 
def registerCalled():
    return render_template("register.html")

@app.route("/login",methods=['POST'])
def login():
    print("attempted")
    userid = request.form['userid']
    password = request.form['password']
    print(userid)
    print(password)
    print(credentials)
    
    if userid in users:
        if password == credentials[userid]:
            return render_template("institutehome.html",user = userid)
    flash("invalid")
    return render_template("login.html")

    

@app.route("/registeruser",methods=['POST']) 
def registerUser():
    print(users)
    name = request.form['name']
    userid = request.form['userid']
    password = request.form['password']
    email = request.form['email']
    address = request.form['address']
    if not name or not userid or not password or not email or not address:
        flash("incomplete")
        return render_template("register.html")

    if userid in users:
        flash("id exists")
        return render_template("register.html")
    else:
        flash("User successfully registered")  
        users.append(userid)  
        credentials[userid]=password
        return render_template("login.html")

def retrieveStudents(str):
    students = []
    temp = ""
    for i in range(len(str)):
        if str[i]==',':
            students.append(temp)
            temp = ""
        else:
            temp+=str[i]
    if not temp:
        students.append(temp)
    return students

@app.route("/addcourse/<id>", methods=['POST'])
def addCourse(id):
    print(id)
    print(type(id))
    course = request.form['course']
    room = request.form['room']
    students = request.form['student_list']
    # days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
    # coursedays = []
    # for day in days:
    #     if request.form[day] != "":
    #         coursedays.append(day)
    coursedays = request.form.getlist("day")
    time = request.form['time']
    duration = request.form['duration']
    # user = request.form['user']
    if not course or not room or not students or not time or not duration or len(coursedays)==0:
        flash("Missing fields")
        return render_template("institutehome.html")
    studentlist = retrieveStudents(students)
    print(course)
    print(room)
    print(studentlist)
    print(coursedays)
    print(time)
    print(duration)
    print("-------")
    inst_id = id
    print(inst_id)
    data = {}
    data["course"]=course
    data["room_number"]=room
    data["students"]=studentlist
    data["days"]=coursedays
    data["attendance_time"]=time
    data["attendance_duration"]=duration
    print(data)
    picklepath = "../static/data/institutes/"
    picklepath = os.path.join(picklepath,id)
    if not path.exists(picklepath):
        os.mkdir(picklepath)
        picklepath = os.path.join(picklepath,"courses") 
        os.mkdir(picklepath)
    
    picklepath += ("/"+course+".pickle")
    
    pickle_out = open(picklepath,"wb")
    pickle.dump(data, pickle_out)
    pickle_out.close()
    return render_template("institutehome.html")


if __name__ == "__main__":        # on running python app.py
    app.run(debug=True) 