$("#submit").click(function() {
    var jid = $("#job_id").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();

    var jr = jid.match("^\\d+$");
    if(jr == null){
        alert("The job id should be a number!");
        return false;
    }

    if((start_time != "" && end_time =="") || (start_time == "" && end_time !="")){
        alert("Please input both start time and end time or none of them");
        return false;
    }
    if(start_time !="" && end_time !=""){
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
    }

    if(!confirm("Please recheck your JOB ID:" + jid)){
        return false;
    }

    $("#div_tip").html("Querying...");
    $.ajax({
        url : "/draw_cmetadata",
        type : 'post',
        data : $('#form_cmetadata').serialize(),
        dataType : 'json',
        success : function(data) {
            var obj = eval(data);
            var rmax = obj.data.rmax;
            var rmin = obj.data.rmin;
            var ravg = obj.data.ravg;
            var rsum = obj.data.rsum;
            var wmax = obj.data.wmax;
            var wmin = obj.data.wmin;
            var wavg = obj.data.wavg;
            var wsum = obj.data.wsum;
            var jobid = obj.data.jobid;

            if (jobid.length == 0){
                jobid=123456
            }
            $("#div_tip").html("Result");
            $("#rmax").html(rmax);
            $("#rmin").html(rmin);
            $("#ravg").html(ravg);
            $("#rsum").html(rsum);
            $("#wmax").html(wmax);
            $("#wmin").html(wmin);
            $("#wavg").html(wavg);
            $("#wsum").html(wsum);
            $('#image').attr('src', '/image/'+jobid+"_cmetadata.png");
        },
        error : function() {
            if(!confirm("Opoos! Some error just happened! Do you want to view the detail error information?")){
                return false;
            }
            location.href = "/c_error?error_file="+jid+"_cmetadata.log";
        }
    })
});
