$("#submit").click(function() {
    var start_time = $("#stime").val();
    var end_time = $("#etime").val();

    if((start_time == ""||end_time =="")){
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
        alert("The start time can not be later than the end time");
        return false;
    }

	$("#btn_tip").text("Querying...");
	$.ajax({
		url : "/lustre_server_data",
		type : 'post',
		data : $('#form_ost').serialize(),
		dataType : 'json',
		success : function(data) {
	        $("#btn_tip").text("Success");
            total_data = 1;
			var obj = eval(data);
            set_draw_data(obj.data);
            draw_ost();
            draw_group();
		},
	});
});

var data_type = 1; // 1:read, 2:write
var total_data = 0; // 1: already get total 440 OSTs info
var draw_data;
var arr_xaxis;
var groupid = 1;
var ostid = 1;

$("#btn_draw_group").click(function(){
    groupid = parseInt($("#ipt_groupid").val());
    check_id(1);
    draw_group();
});

$("#btn_draw_ost").click(function(){
    ostid = parseInt($("#ipt_ostid").val());
    check_id(2);
    draw_ost();
});

function get_total_data(){
	$.ajax({
		url : "/lustre_server_data",
		type : 'post',
		data : $('#form_ost').serialize(),
		dataType : 'json',
		success : function(data) {
	        $("#btn_tip").text("Success");
            total_data = 1;
			var obj = eval(data);
            set_draw_data(obj.data);
            draw_ost();
            draw_group();
		},
	});
}

function read_write(){
    if($("#btn_rw").text() == "Read"){
        $("#btn_rw").text("Write");
        data_type = 2;
        draw_group();
    }else{
        $("#btn_rw").text("Read");
        data_type = 1;
        draw_group();
    }
}

function set_draw_data(data){
    draw_data = data;
    console.log(typeof draw_data.iobw_r);
    arr_xaxis = draw_data.arr_xaxis;
    groupid = 1;
    ostid = 1;
}

//1:group_id 2:ostid
function check_id(type){
    if(type == 1){
        if(parseInt($("#ipt_groupid").val()) < 1){
            $("#ipt_groupid").val(1);
            groupid = 1;
        }else if(parseInt($("#ipt_groupid").val()) > 72){
            $("#ipt_groupid").val(72);
            groupid = 72;
        }else{
            groupid = parseInt($("#ipt_groupid").val());
        }
    }else if(type == 2){
        if(parseInt($("#ipt_ostid").val()) < 1){
            $("#ipt_ostid").val(1);
            ostid = 1;
        }else if(parseInt($("#ipt_ostid").val()) > 440){
            $("#ipt_ostid").val(440);
            ostid = 440;
        }else{
            ostid = parseInt($("#ipt_ostid").val());
        }
    }
}

function group_prev(){
    event.stopPropagation();
    groupid -= 1;
    $("#ipt_groupid").val(groupid.toString());
    check_id(1);
    draw_group();
}

function group_next(){
    event.stopPropagation();
    groupid += 1;
    $("#ipt_groupid").val(groupid.toString());
    check_id(1);
    draw_group();
}

function ost_prev(){
    event.stopPropagation();
    ostid -= 1;
    $("#ipt_ostid").val(ostid.toString());
    check_id(2);
    draw_ost();
}

function ost_next(){
    event.stopPropagation();
    ostid += 1;
    $("#ipt_ostid").val(ostid.toString());
    check_id(2);
    draw_ost();
}

function draw_ost(){
    $("#ipt_ostid").val(ostid.toString());
    if(typeof(draw_data) == "undefined"){
        alert("Please query and get data first");
        return false;
    }

    var myChart = echarts.init(document.getElementById('echarts_ost'));
    var option = {
        tooltip: {trigger:'axis', position:function(pt){return [pt[0], '10%'];}},

        //toobox: {feature:{dataZoom:{yAxisIndex:'none'},}},
        legend: {
            orient: 'vertical',
            right: '8%',
        },

        xAxis: {type:'category', boundaryGap:false, data:arr_xaxis},

        yAxis: {type:'value', name:'Bandwidth (MB/s)', boundaryGap:[0, '100%']},

        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 50
        },{
            start: 0,
            end: 60,
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
                color: '#fff',
                shadowBlur: 3,
                shadowColor: 'rgba(0, 0, 0, 0.6)',
                shadowOffsetX: 2,
                shadowOffsetY: 2,
            }
        }],

        series: [
            {name:'read bandwidth', type:'line', smooth:true, symbol:'none', itemStyle:{normal:{color:'red'}}, data:draw_data.iobw_r[ostid - 1]},
            {name:'write bandwidth', type:'line', smooth:true, symbol:'none', itemStyle:{normal:{color:'blue'}}, data:draw_data.iobw_w[ostid - 1]},
        ]
   };
   myChart.setOption(option);
}

function draw_group(){
    $("#ipt_groupid").val(groupid.toString());
    if(typeof(draw_data) == "undefined"){
        alert("Please query and get data first");
        return false;
    }

    ostid = (groupid - 1) * 6 + 1;
    draw_ost();

    var iobw_data;
    var mtitle = "Read";
    if(data_type == 1){
       iobw_data = draw_data.iobw_r; 
    }else if(data_type == 2){
       iobw_data = draw_data.iobw_w; 
       mtitle = "Write" 
    }

    var start = (groupid - 1) * 6; 
    var pageChart = echarts.init(document.getElementById('echarts_ost_group'));
    var y_op = {rotate: -40}
    var option = {
        tooltip: {trigger:'axis', position:function(pt){return [pt[0], '10%'];}},

        grid: [{y:'5%', height:'14%'}, {y:'20%', height:'14%'},{y:'35%', height:'14%'}, {y:'50%', height:'14%'}, {y:'65%', height:'14%'}, {y:'80%', height:'14%'}],

        title: {left:'center', text:mtitle + ' Bandwidth (MB/s)'},

        xAxis: [
            {show:false, type:'category', gridIndex:0, data: arr_xaxis},
            {show:false, type:'category', gridIndex:1, data: arr_xaxis},
            {show:false, type:'category', gridIndex:2, data: arr_xaxis},
            {show:false, type:'category', gridIndex:3, data: arr_xaxis},
            {show:false, type:'category', gridIndex:4, data: arr_xaxis},
            {show: true, type:'category', gridIndex:5, data: arr_xaxis}
        ],

        yAxis: [
            {show:true, type:'value', gridIndex:0, min:0, max:350, name:'OST ' + (start + 1), nameLocation:'middle', nameGap:40},
            {show:true, type:'value', gridIndex:1, min:0, max:350, name:'OST ' + (start + 2), nameLocation:'middle', nameGap:40},
            {show:true, type:'value', gridIndex:2, min:0, max:350, name:'OST ' + (start + 3), nameLocation:'middle', nameGap:40},
            {show:true, type:'value', gridIndex:3, min:0, max:350, name:'OST ' + (start + 4), nameLocation:'middle', nameGap:40},
            {show:true, type:'value', gridIndex:4, min:0, max:350, name:'OST ' + (start + 5), nameLocation:'middle', nameGap:40},
            {show:true, type:'value', gridIndex:5, min:0, max:350, name:'OST ' + (start + 6), nameLocation:'middle', nameGap:40},
        ],

        series: [
            {type:'line', xAxisIndex: 0, yAxisIndex: 0, smooth: true, data: iobw_data[start + 0]},
            {type:'line', xAxisIndex: 1, yAxisIndex: 1, smooth: true, data: iobw_data[start + 1]},
            {type:'line', xAxisIndex: 2, yAxisIndex: 2, smooth: true, data: iobw_data[start + 2]},
            {type:'line', xAxisIndex: 3, yAxisIndex: 3, smooth: true, data: iobw_data[start + 3]},
            {type:'line', xAxisIndex: 4, yAxisIndex: 4, smooth: true, data: iobw_data[start + 4]},
            {type:'line', xAxisIndex: 5, yAxisIndex: 5, smooth: true, data: iobw_data[start + 5]}
        ]
    };
    pageChart.setOption(option);
}
