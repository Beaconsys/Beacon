$("#submit").click(function() {
    var jobid = $("#ipt_jobid").val();
    var start_time = $("#ipt_stime").val();
    var end_time = $("#ipt_etime").val();
    var query_type = $("#query_type option:selected").text();

    var jr = jobid.match("^\\d+$");
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
    $("#div_tip").html("Querying...");

    $.ajax({
        url : "/lwfs_client_data",
        type : 'post',
        data : $('#form_lwfs_client').serialize(),
        dataType : 'json',
        success : function(data) {
            $("#div_tip").html("Success");
            $("#btn_draw").attr("disabled", false);
            $("#query_type").attr("disabled", false);
            var obj = eval(data);
            var query_data = obj.data;
            set_query_data(query_data);
            draw(draw_data, arr_xaxis);
        }})
});

$("#btn_draw").click(function(){
    draw(draw_data, arr_xaxis);

});
//1:iobw_r, 2:iobw_w, 3:iops_r, 4:iops_w, 5:file_open, 6:file_close
var data_type = 1;
var query_data;
var arr_xaxis;
var draw_data;

function set_query_data(data){
    query_data = data;
    arr_xaxis = query_data.arr_xaxis;
    draw_data = query_data.iobw_r;
}

function change_query_type(){
    var query_type = $("#query_type option:selected").text();
    switch(query_type){
        case "read bandwidth":
            data_type = 1;
            draw_data = query_data.iobw_r;
            draw(draw_data, arr_xaxis);
            break;
        case "write bandwidth":
            data_type = 2;
            draw_data = query_data.iobw_w;
            draw(draw_data, arr_xaxis);
            break;
        case "read iops":
            data_type = 3;
            draw_data = query_data.iops_r;
            draw(draw_data, arr_xaxis);
            break;
        case "write iops":
            data_type = 4;
            draw_data = query_data.iops_w;
            draw(draw_data, arr_xaxis);
            break;
        case "file open":
            data_type = 5;
            draw_data = query_data.file_open;
            draw(draw_data, arr_xaxis);
            break;
        case "file close":
            data_type = 6;
            draw_data = query_data.file_close;
            draw(draw_data, arr_xaxis);
            break;
    }
}

function draw(draw_data, arr_xaxis){
    var tip = "";
    switch(data_type){
        case 1:
            tip = "Read I/O Bandwidth (MB/s) ";
            break;
        case 2:
            tip = "Write I/O Bandwidth (MB/s) ";
            break;
        case 3:
            tip = "Read IOPS ";
            break;
        case 4:
            tip = "Write IOPS ";
            break;
        case 5:
            tip = "File Open ";
            break;
        case 6:
            tip = "File Close ";
            break;
    }
    var myChart = echarts.init(document.getElementById("mchart"));
    var option = {
        tooltip: {
            trigger: 'axis',
            position: function (pt) {
                return [pt[0], '10%'];
            }
        },
        title: {
            left: 'center',
            text: tip
        },
        toobox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none' 
                },
                retore: {},
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: arr_xaxis
        },
        yAxis: {
            type: 'value',    
        },
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
        series: [{
            name: tip,
            type: 'line',
            smooth: true,
            symbol: 'none',
            itemStyle: {
                normal: {
                    color: 'rgb(255, 70, 131)'
                }
            },
            areaStyle: {
                normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgb(255, 158, 68)'
                    }, {
                        offset: 1,
                        color: 'rgb(255, 70, 131)'
                    }])
                }
            },
            data: draw_data
        }]
    };
    myChart.setOption(option);
}
