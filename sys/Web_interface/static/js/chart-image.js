$("#submit").click(function() {
	var jid = $("#job_id").val();
	if(!confirm("Please recheck your JOB ID:" + jid)){
		return false;
	}
	$("#div_tip").html("Querying...");
	$.ajax({
		url : "/draw",
		type : 'post',
		data : $('#form_iops').serialize(),
		dataType : 'json',
		success : function(data) {
			var obj = eval(data);
			var jobid = obj.data.jobid;
			if (jobid.length == 0){
				jobid=123456
			}
			$("#div_tip").html("Result");			
			$('#image').attr('src', '/image/'+jobid)
		},
		error : function() {
			alert("error")
		}
	})
});
