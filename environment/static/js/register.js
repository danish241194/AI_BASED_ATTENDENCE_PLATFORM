function registerClicked(){
    var userId = document.getElementById("user_id").value;
    var password = document.getElementById("password_id").value;
    var type = document.getElementById("type_id").value;
    var name = document.getElementById("name_id").value;
    var email = document.getElementById("email_id").value;
    var address = document.getElementById("address_id").value;
    var obj = {type:type, name:name, userId:userId, password:password, email:email, address:address}
    var data = {data:obj};
    var url_String = "localhost:5000/registeruser"
    // alert("ASdsd")
    // $.ajax({
    //     type: "POST",
    //     url: url_String,
    //     data: "JSON.stringify(data)",
    //     dataType: "json",
    //     crossDomain: true,
    //     success: function() { alert("Success"); },
    //     error: function() { alert('Failed!'); },
    //     headers: {

    //     }
    // });



}