function check(form){
    var start_time = form.start_time.value;
    var end_time = form.end_time.value;

    if (start_time == "" || end_time == ""){
        alert("Please input both start time and end time");
        return false;
    }

    var reg = /^(\d{1,4})(-|\/)(\d{1,2})\2(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})$/;
    var sr = start_time.match(reg);
    var er = end_time.match(reg);
    
    if(sr == null){
        alert("Please input the right format start time, e.g. 2017-04-03 08:00:00");
        return false;
    }      
    
    if(er == null){
       alert("Please input the right format end time, e.g. 2017-04-03 08:00:00");
       return false; 
    }

    if(start_time >= end_time){
        alert("The start time can not  be later than the end time");
        return false;
    }

    return true;
}



