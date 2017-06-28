
function getCon() {
//	alert("hel");
	$.ajax({
		url:'allowcons/',
		contentType: "application/json",
		success:function(json){
//			alert("hell");
			if(json['status']=='failure'){
				$('#cons').html("No contest requests.");
				return;
			}
			html = "";
			for (data in json){
				html+="<div id="+json[data]['pk']+">";
				html += "Name: "+json[data].fields.name+"<br>";
				html += "Code: "+json[data].fields.contest_code+"<br>";
				html += "Start: "+json[data].fields.start_date+"<br>";
				html += "End: "+json[data].fields.end_date+"<br>";
				html += "<button onclick='allow(1, "+ json[data].pk +")'> Allow </button><button onclick='allow(0, "+ json[data].pk+")'> Reject </button>";
				html += "</div>";
			}
			$('#cons').html(html);
		},
		error: function(e){
			$('#cons').html("No contest requests.");
		}
	});
}

function allow(a, pk) {
	$.ajax({
		type:'GET',
		url:'allow/',
		data: 'ag='+a+"&pk="+pk,
		contentType: "application/json",
		success:function(json){
			alert("congratulations.");
		},
		error: function(e){
			alert("Request Failure. Probably because you're not allowed or because of Internet Connection");
		}
	});
}