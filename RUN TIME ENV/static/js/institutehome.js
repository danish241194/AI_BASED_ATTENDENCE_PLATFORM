requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: 'js/lib',
    //except, if the module ID starts with "app",
    //load it from the js/app directory. paths
    //config is relative to the baseUrl, and
    //never includes a ".js" extension since
    //the paths config could be for a directory.
    paths: {
        app: '../js'
    }
});




function addStudents(){

}

function removeStudents(){

}

function addCamera(){

}

function addCourse(){
    var coursename = document.getElementById("course_id").value;
    var room = document.getElementById("course_room_id").value;
    var roll = document.getElementById("course_studentlist_id").value;
    var time = document.getElementById("time_id").value;
    var duration  = document.getElementById("duration_id").value;
    console.log(coursename)
    console.log(room)
    console.log(roll)
    console.log(time)
    console.log(duration)
    if(coursename=="" || room=="" || roll=="" || time=="" || duration==""){
        alert("Missing Fields");
        return;
    }
    var days = [];
    if(document.getElementById("sunday_id").checked==true)
        days.push("sunday");
    if(document.getElementById("monday_id").checked==true)
        days.push("monday");
    if(document.getElementById("tuesday_id").checked==true)
        days.push("tuesday");
    if(document.getElementById("wednesday_id").checked==true)
        days.push("wednesday");
    if(document.getElementById("thursday_id").checked==true)
        days.push("thusday");
    if(document.getElementById("friday_id").checked==true)
        days.push("friday");
    if(document.getElementById("saturday_id").checked==true)
        days.push("saturday");
    if(days.length==0){
        alert("Pick atleast one day")
        return;
    }
    const fs = require('fs')
    var instituteid = inst1;
    var path = "../data/"+instituteid+coursename+".json";
    console.log(path);
    // fs.writeFile(path,)
    console.log(days);



}