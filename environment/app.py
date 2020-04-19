from flask import Flask,render_template
from flask import Flask, flash, request, redirect, render_template, make_response, url_for
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
ALLOWED_EXTENSIONS = set(['zip'])

users = []
credentials = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def retrieveListFromString(str_):
    return str_.split(",")

@app.route("/viewcameras/<id>")
def viewCamera(id):
    pathtofile = './static/data/institutes'
    pathtofile = os.path.join(pathtofile,id)
    pathtofile = os.path.join(pathtofile,"cameras")
    if not path.exists(pathtofile):
        flash("nocameras")
        return render_template("institutehome.html",user = id)
    entries = os.listdir(pathtofile)
    cameralist = []
    for entry in entries:
        dbfile = open(pathtofile+"/"+entry,'rb')
        db = pickle.load(dbfile)
        temp = {}
        for key in db:
            temp[key] = db[key]
        dbfile.close()
        cameralist.append(temp)
    data = {}
    data["cameras"] = cameralist
    print(data)
    return render_template("institutecameras.html",data = data)

@app.route("/viewcourses/<id>")
def viewCourses(id):
    pathtofile = './static/data/institutes'
    pathtofile = os.path.join(pathtofile,id)
    pathtofile = os.path.join(pathtofile,"courses")
    if not path.exists(pathtofile):
        flash("nocourses")
        return render_template("institutehome.html",user = id)
    entries = os.listdir(pathtofile)
    courselist = []
    for entry in entries:
        dbfile = open(pathtofile+"/"+entry,'rb')
        db = pickle.load(dbfile)
        temp = {}
        for key in db:
            if key=="students":
                continue
            temp[key] = db[key]
        dbfile.close()
        courselist.append(temp)
    data = {}
    data["courses"] = courselist
    print(data)
    return render_template("institutecourses.html",data = data)

@app.route("/addcamera/<id>",methods=['POST'])
def addCamera(id):
    room = request.form['room']
    camera_id = request.form['camera_id']
    if not room or not camera_id:
        flash("Missing fields")
        return render_template("institutehome.html",user = id)
    else: 
        picklepath = "static/data/institutes/"
        picklepath = os.path.join(picklepath,id)  
        if not path.exists(picklepath):
            os.mkdir(picklepath)
        picklepath = os.path.join(picklepath,"cameras")  
        if not path.exists(picklepath):
            os.mkdir(picklepath)

        
        picklepath += ("/"+camera_id+".pickle")
        pickle_out = open(picklepath,"wb")
        api="http://127.0.0.1:5004/"
        api+= id+"_"+room+"_"+camera_id
        data = {"api":api,"room":room,"camera_id":camera_id}
        print(data)
        pickle.dump(data, pickle_out)
        pickle_out.close() 
        flash("Camera successfully Added")
        data_to_sensor_manager = {"institute_id":id,"cameras" :[{"camera_id":camera_id,"room_id":room}]}
        req = requests.post("http://localhost:5004/institute/add_camera",json=data_to_sensor_manager)
        return render_template("institutehome.html",user = id)

@app.route("/<id>",methods=['POST'])
def addStudents(id):
    if "file" not in request.files:
        flash("No file part")
        return render_template("institutehome.html",user = id)

    file = request.files['file']
    filename = file.filename
    if file.filename == '':
        flash('No file selected for uploading')
    elif file and allowed_file(file.filename):
        file.save( 'images/'+filename)
        os.system("unzip images/"+filename +" -d images")
        os.system("rm images/"+filename)
        req = requests.post("http://localhost:5003/deployment/service/train_users",json={"org":"institute","id":id,"zip_location":filename.split(".")[0]})
        flash('File successfully uploaded')
    else:
        flash('Allowed file types are zip')
    return render_template("institutehome.html",user = id)

@app.route("/removestudents/<id>",methods=['POST'])
def removeStudents(id):
    students_string = request.form['removelist']
    if not students_string:
        flash("Missing fields")
        return render_template("institutehome.html",user = id)
    print(students_string)
    students = retrieveListFromString(students_string)
    data_to_dep = {"institute_id":id,"roll_numbers":students}
    req = requests.post("http://localhost:5003/deployment/service/remove_users",json=data_to_dep)
    flash("Removed successfully")

    return render_template("institutehome.html",user = id)


@app.route("/addcourse/<id>", methods=['POST'])
def addCourse(id):
    print(id)
    course = request.form['course']
    room = request.form['room']
    students = request.form['student_list']
    
    print(students)
    coursedays = request.form.getlist("day")
    time = request.form['time']
    duration = request.form['duration']
    if not course or not room or not students or not time or not duration or len(coursedays)==0:
        flash("Missing fields")
        return render_template("institutehome.html",user = id)
    studentlist = retrieveListFromString(students)
    print(studentlist)
    data = {}
    data["course"]=course
    data["room_number"]=room
    data["students"]=studentlist
    data["days"]=coursedays
    data["attendance_time"]=time
    data["attendance_duration"]=duration
    print(data)
    picklepath = "static/data/institutes/"
    picklepath = os.path.join(picklepath,id)  
    if not path.exists(picklepath):
        os.mkdir(picklepath)
    picklepath = os.path.join(picklepath,"courses")  
    if not path.exists(picklepath):
        os.mkdir(picklepath) 
    
    picklepath += ("/"+course+".pickle")
    pickle_out = open(picklepath,"wb")
    pickle.dump(data, pickle_out)
    pickle_out.close()
    flash("Course registered")
    scheduling_data = {}
    '''
            "institute_id":"ins id"
            "room_id":"room id"
            "course_no":"cs1234"
            "day":"monday"
            "start_time":"13:00"
            "attendence_minutes":10
            ""
        '''
    scheduling_data["institute_id"] = id
    scheduling_data["room_id"] = room
    scheduling_data["course_no"] = course
    scheduling_data["start_time"] = str(time)
    scheduling_data["attendence_minutes"] = int(duration)
    for day in coursedays:
        scheduling_data["day"] = day.lower()
        print("\n\nAPI TO SCHEDULING DATA\n",scheduling_data)
        requests.post("http://localhost:8899/schedule/startSchedule",json=scheduling_data)
    return render_template("institutehome.html",user = id)

@app.route("/iqm/<id>")
def renderQueryManager(id):
    print(id)
    return render_template("institutequery.html",user = id)


def convertDate(date):
    for i in range(len(date)):
        if date[i]=='/':
            date[i]='-'
    return date

@app.route("/institutequery/<id>",methods=['POST','GET'])
def instituteQuery(id):
    if not request.form :
        return render_template("institutequery.html",user=id )
    coursestring = request.form['courselist']
    studentstring = request.form['studentlist']
    startdate = request.form['start']
    enddate = request.form['end']
    criterion = request.form['criterion']
    if not startdate or not enddate or not criterion or len(coursestring)==0 or len(studentstring)==0:
        flash("incomplete")
        return redirect(url_for("instituteQuery",id=id))
        # return render_template("institutequery.html",user=id )
    courses = retrieveListFromString(coursestring)
    students = retrieveListFromString(studentstring)
    query = {}
    query["courses"] = courses
    query["students"] = students
    query["start_date"] = convertDate(startdate)
    query["end_date"] = convertDate(enddate)
    if criterion != 0:
        temp = {}
        temp["greater_than"] = criterion
        query["condition"] = temp
    else:
        query["condition"] = None

    request_data = {}
    request_data["institute_id"]=id
    request_data["query"] = query
    print(request_data)
    return render_template("institutequery.html",user=id )


if __name__ == "__main__":        # on running python app.py
    app.run(debug=True) 