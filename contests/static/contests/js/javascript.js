function del(code){
	var answer = confirm("Are you sure to delete the question "+code+"?");
	if(answer){
		$.ajax({
			type:'get',
			url:"/contests/q/delete/"+code+"/",
			success:function(data){
				location.reload();
			},
			error: function(data){
				alert("request failure");
			}
		});
	}
}

$(document).ready(function( ){
	var dts = document.getElementsByClassName("datetime");

	for(var i = 0;i < dts.length; i++){
		date = dts[i].getElementsByClassName("vDateField")[0];
		time = dts[i].getElementsByClassName("vTimeField")[0];
		date.type= "date";
		time.type = "time";
	}
});

function delCon(){
	var answer = confirm("Are you sure to delete this Contest?");
	if(answer){
		$.ajax({
			type:'get',
			url:'/contests/q/'+document.getElementById("code").getAttribute('value')+'/delete/',
			success:function(date){
				location.href = "/contests/";
			},
			error:function(data){
				alert("Couldn't delete because"+data);
			}
		});
	}
}

function showForm(){
	var btn = document.getElementById("showform");
	var ele = btn.parentElement;
	ele.removeChild(btn);
	str = ele.innerHTML;
//	alert(ele.innerHTML);
	html = "<form action='.' method=post>"+str+"<label for='com'>Comment:</label><br> <textarea name='com' rows=10 required ></textarea><br><input type=submit /></form><br><hr>";
	ele.innerHTML = html;
}
