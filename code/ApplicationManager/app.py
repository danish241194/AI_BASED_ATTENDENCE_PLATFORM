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
corporatestart = []
def get_ip_port(service):
    res = requests.get("http://172.17.0.1:5533/get_service_location/"+service)
    return (res.json())["ip"]+":"+str((res.json())["port"])

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

def convertDate(date):
    new_Date = date.split("-")
    date = str(new_Date[2])+"-"+str(new_Date[1])+"-"+str(new_Date[0])
    return date

@app.route("/") 
def home():
    return render_template("login.html")

@app.route("/register") 
def registerCalled():
    return render_template("register.html")
@app.route('/health')
def health():
    return {"res":"live"}
@app.route("/login",methods=['POST'])
def login():
    print("attempted")
    userid = request.form['userid']
    password = request.form['password']
    print(userid)
    print(password)
    print(credentials)
    
    if userid in users:
        credentials[userid]
        if password == credentials[userid][0]:
            if credentials[userid][1] == "institute":
                return render_template("institutehome.html",user = userid)
            else:
                if userid in corporatestart:
                    return render_template("corporatehome.html",user = userid, start = 1)
                else:
                    return render_template("corporatehome.html",user = userid, start = 0)
    flash("invalid")
    return render_template("login.html")


@app.route("/startclicked/<id>",methods=['POST'])
def startClicked(id):    
    if id in corporatestart: 
        corporatestart.remove(id)
    print("removed")
    print(corporatestart)
    response = {"org":"corporate","corporate_id":id}
    print("SENDING REQUEST TO DEP. MANAGER TO START ATTENDENCE")
    res = requests.post('http://172.17.0.1:5003/deployment/service/start_attendence', json=response)
    if id in corporatestart:
        return render_template("corporatehome.html",user = id, start = 1)
    else:
        return render_template("corporatehome.html",user = id, start = 0)

@app.route("/registeruser",methods=['POST']) 
def registerUser():
    print(users)
    type = request.form['type']
    name = request.form['name']
    userid = request.form['userid']
    password = request.form['password']
    email = request.form['email']
    address = request.form['address']
    print(type)
    if not name or not userid or not password or not email or not address:
        flash("incomplete")
        return render_template("register.html")

    if userid in users:
        flash("id exists")
        return render_template("register.html")

    flash("User successfully registered")  
    users.append(userid)
    if type=="corporate":
        corporatestart.append(userid)
    temp = [password,type]
    credentials[userid]=temp
    return render_template("login.html")

def retrieveListFromString(str_):
    return str_.split(",")

@app.route("/viewinstitutecameras/<id>")
def viewInstituteCamera(id):
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


@app.route("/viewcorporatecameras/<id>")
def viewCorporateCamera(id):
    pathtofile = './static/data/corporates'
    pathtofile = os.path.join(pathtofile,id)
    pathtofile = os.path.join(pathtofile,"cameras")
    if not path.exists(pathtofile):
        flash("nocameras")
        if id in corporatestart:
            return render_template("corporatehome.html",user = id, start = 1)
        else:
            return render_template("corporatehome.html",user = id, start = 0)

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
    return render_template("corporatecameras.html",data = data)

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

@app.route("/addinstitutecamera/<id>",methods=['POST'])
def addInstituteCamera(id):
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
        api="http://172.17.0.1:5004/upload_image/"
        api+= id+"_"+room+"_"+camera_id
        data = {"camera_id":camera_id,"room":room,"api":api}
        print(data)
        pickle.dump(data, pickle_out)
        pickle_out.close() 
        flash("Camera successfully Added")
        data_to_sensor_manager = {"institute_id":id,"cameras" :[{"camera_id":camera_id,"room_id":room}]}
        sensor_ip_port = get_ip_port("Sensor Manager")
        req = requests.post("http://"+sensor_ip_port+"/institute/add_camera",json=data_to_sensor_manager)
        return render_template("institutehome.html",user = id)


#complete api part and testing
@app.route("/addcorporatecamera/<id>",methods=['POST'])
def addCorporateCamera(id):
    gate = request.form['gate']
    camera_id = request.form['camera']
    type = request.form['type']
    if not gate or not camera_id or not type:
        flash("Missing fields")
        if id in corporatestart:
            return render_template("corporatehome.html",user = id, start = 1)
        else:
            return render_template("corporatehome.html",user = id, start = 0)
    else: 
        picklepath = "static/data/corporates/"
        picklepath = os.path.join(picklepath,id)  
        if not path.exists(picklepath):
            os.mkdir(picklepath)
        picklepath = os.path.join(picklepath,"cameras")  
        if not path.exists(picklepath):
            os.mkdir(picklepath)

        
        picklepath += ("/"+camera_id+".pickle")
        pickle_out = open(picklepath,"wb")
        api=""
        if(type=="IN"):
            api="http://172.17.0.1:5004/upload_image_corporate/"+id+"_"+"IN"
        else:
            api="http://172.17.0.1:5004/upload_image_corporate/"+id+"_"+"OUT"

        data = {"camera_id":camera_id,"gate":gate,"type":type,"api":api}
        
        print(data)
        
        pickle.dump(data, pickle_out)
        pickle_out.close() 
        flash("Camera successfully Added")
        data_to_SM = {"corporate_id":id,"cameras":[{"camera_id":camera_id,"type":type}]}
        # data_to_sensor_manager = {"institute_id":id,"cameras" :[{"camera_id":camera_id,"room_id":room}]}
        sensor_ip_port = get_ip_port("Sensor Manager")

        req = requests.post("http://"+sensor_ip_port+"/corporate/add_camera",json=data_to_SM)
        print(corporatestart)
        if id in corporatestart:
            return render_template("corporatehome.html",user = id, start = 1)
        else:
            return render_template("corporatehome.html",user = id, start = 0)

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
        req = requests.post("http://172.17.0.1:5003/deployment/service/train_users",json={"org":"institute","id":id,"zip_location":filename.split(".")[0]})
        flash('File successfully uploaded')
    else:
        flash('Allowed file types are zip')
    return render_template("institutehome.html",user = id)

##change api due to clash with addStudents api
@app.route("/addemployees/<id>",methods=['POST'])
def addEmployees(id):
    if "file" not in request.files:
        flash("No file part")
        if id in corporatestart:
            return render_template("corporatehome.html",user = id, start = 1)
        else:
            return render_template("corporatehome.html",user = id, start = 0)

    file = request.files['file']
    filename = file.filename
    if file.filename == '':
        flash('No file selected for uploading')
    elif file and allowed_file(file.filename):
        file.save( 'images/'+filename)
        os.system("unzip images/"+filename +" -d images")
        os.system("rm images/"+filename)
        req = requests.post("http://172.17.0.1:5003/deployment/service/train_users",json={"org":"corporate","id":id,"zip_location":filename.split(".")[0]})
        flash('File successfully uploaded')
    else:
        flash('Allowed file types are zip')
    if id in corporatestart:
        return render_template("corporatehome.html",user = id, start = 1)
    else:
        return render_template("corporatehome.html",user = id, start = 0)

@app.route("/removestudents/<id>",methods=['POST'])
def removeStudents(id):
    students_string = request.form['removelist']
    if not students_string:
        flash("Missing fields")
        return render_template("institutehome.html",user = id)
    print(students_string)
    students = retrieveListFromString(students_string)
    data_to_dep = {"institute_id":id,"roll_numbers":students}
    req = requests.post("http://172.17.0.1:5003/deployment/service/remove_users",json=data_to_dep)
    flash("Removed successfully")
    if id in corporatestart:
        return render_template("institutehome.html",user = id, start = 1)
    else:
        return render_template("institutehome.html",user = id, start = 0)


## backend api needs to change
@app.route("/removeemployees/<id>",methods=['POST'])
def removeEmployees(id):
    employee_string = request.form['removelist']
    if not employee_string:
        flash("Missing fields")
        if id in corporatestart:
            return render_template("corporatehome.html",user = id, start = 1)
        else:
            return render_template("corporatehome.html",user = id, start = 0)
    print(employee_string)
    students = retrieveListFromString(employee_string)
    data_to_dep = {"institute_id":id,"roll_numbers":students}
    req = requests.post("http://172.17.0.1:5003/deployment/service/remove_users",json=data_to_dep)
    flash("Removed successfully")

    if id in corporatestart:
        return render_template("corporatehome.html",user = id, start = 1)
    else:
        return render_template("corporatehome.html",user = id, start = 0)


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
        scheduler_ip_port = get_ip_port("Scheduler")
        res = requests.post("http://"+scheduler_ip_port+"/schedule/startSchedule",json=scheduling_data)
        print(res.json())
    return render_template("institutehome.html",user = id)

@app.route("/iqm/<id>")
def renderInstituteQueryManager(id):
    print(id)
    return render_template("institutequery.html",user = id)


@app.route("/cqm/<id>")
def renderCorporateQueryManager(id):
    print(id)
    return render_template("corporatequery.html",user = id)


@app.route("/institutequery/<id>",methods=['POST','GET'])
def instituteQuery(id):
    if not request.form :
        return render_template("institutequery.html",user=id )
    coursestring = request.form['courselist']
    studentstring = request.form['studentlist']
    startdate = request.form['start']
    enddate = request.form['end']
    criterion = request.form['criterion']
    if not startdate or not enddate or not criterion or not coursestring or not studentstring:
        flash("incomplete")
        return redirect(url_for("instituteQuery",id=id))
        # return render_template("institutequerys.html",user=id )
    courses = retrieveListFromString(coursestring)
    students = retrieveListFromString(studentstring)
    query = {}
    query["courses"] = courses
    query["students"] = students
    query["start_date"] = convertDate(startdate)
    query["end_date"] = convertDate(enddate)
    if int(criterion) != 0:
        temp = {}
        temp["greater_than"] = int(criterion)
        query["condition"] = temp
    else:
        query["condition"] = None

    request_data = {}
    request_data["institute_id"]=id
    request_data["query"] = query
    print(request_data)
    query_ip_port = get_ip_port("Query Manager")
    req = requests.post("http://"+query_ip_port+"/institute/get_attendance",json=request_data)
    out = req.json()
    if(int(criterion)!=0):
        return render_template("instiqueryresults.html",condition=1,data=out)
    else:
        return render_template("instiqueryresults.html",condition=0,data=out)

## make json data for backened API
@app.route("/corporatequery/<id>",methods=['POST','GET'])
def corporateQuery(id):
    if not request.form :
        return render_template("corporatequery.html",user=id )
    employeetring = request.form['employeelist']
    startdate = request.form['start']
    enddate = request.form['end']
    effectivetime = request.form['efftime']
    hourscriterion = request.form['hoursrequired']
    if not startdate or not enddate or not effectivetime or not employeetring or not hourscriterion:
        flash("incomplete")
        return redirect(url_for("corporateQuery",id=id))
    employees = retrieveListFromString(employeetring)

    ## dummy data for view
    query = {}
    query["start_date"] = convertDate(startdate)
    query["end_date"] = convertDate(enddate)

    if int(effectivetime) != 0:
        query["effective_time"]=str(effective_time)+":00:00"
    if int(hourscriterion) != 0:
        temp = {}
        temp["greater_than"] = int(hourscriterion)
        query["condition"] = temp


    request_data = {}
    request_data["corporate_id"]=id
    request_data["ids"] = employees
    request_data["query"] = query
    print(request_data)
    query_ip_port = get_ip_port("Query Manager")

    req = requests.post("http://"+query_ip_port+"/corporate/get_attendance",json=request_data)
    out = req.json()
    if id in corporatestart:
        return render_template("corpqueryresults.html",condition=1,data=out)
    else:
        return render_template("corpqueryresults.html",condition=0,data=out)




    # temp = []
    # for i in range(50):
    #     temp.append("Employee" + str(i))
    # data["employees"] = temp
    # print(data)
    # return render_template("corpqueryresults.html",condition=1,data=data);





if __name__ == "__main__":        # on running python app.py
    app.run(host="0.0.0.0",debug=True) 