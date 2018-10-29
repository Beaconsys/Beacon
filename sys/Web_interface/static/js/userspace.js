function check(form){
    var start_time = form.start_time.value;
    var end_time = form.end_time.value;
    var username = form.username.value;
    
    if (username == ""){
        alert("Please input at least the username");
        return false;
    }

    if((start_time != "" && end_time =="") || (start_time == "" && end_time !="") ){
        
    }

    var reg = /^(\d{1,4})(-|\/)(\d{1,2})\2(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$/;
    
    if(start_time != ""){
        var sr = start_time.match(reg);
        if(sr == null){
            alert("Please input the right format start time, e.g. 2017-04-03 08:00:00");
            return false;
        } 
    }

    if(end_time != ""){
        var sr = end_time.match(reg);
        if(sr == null){
            alert("Please input the right format end time, e.g. 2017-04-03 08:00:00");
            return false;
        } 
    }
    
    if(start_time != "" && end_time !=""){
        if(start_time >= end_time){
            alert("The start time can not  be later than the end time");
            return false;
        }
    }
   
    return true;
}



