function check(form){

    var username = form.username.value;
    var jobname = form.jobname.value;
    
    if (username == "" || jobname == "" ){
        alert("Please input both username and jobname");
        return false;
    }
    return true;
}



