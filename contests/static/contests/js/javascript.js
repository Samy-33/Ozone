
function getTests(){
	
	var n = parseInt(document.getElementById('id_n_testfiles').value);
	document.getElementsByTagName("form")[0].setAttribute('enctype', "multipart/form-data");
	var tests = document.getElementById("tests");
	for(var i = 0; i < n; i++){
		html = "<tr><td> Input "+i+": </td><td><input name=in"+i+".txt required type=file /></td><td> Output "+i+": </td><td><input name=out"+i+".txt required type=file /></td></tr>";
		$('#tests').append(html);
	}
	var button = document.getElementById("sbmt");
	button.removeAttribute("onclick");
	button.setAttribute("type", "submit");
	button.setAttribute("form", "addq");
	button.value="submit";
	button.innerHTML = "Submit";
}

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

