from flask import Flask,render_template
from flask import Flask, flash, request, redirect, render_template, make_response
import urllib.request
import requests   
import os
import json
import codecs
from flask import send_from_directory
from flask_cors import CORS
from functools import wraps



app = Flask(__name__)
cors = CORS(app)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt','json','zip'])

users = []

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
        return render_template("login.html")



if __name__ == "__main__":        # on running python app.py
    app.run(debug=True) 