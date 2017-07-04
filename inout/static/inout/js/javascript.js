
function getCon() {
	$.ajax({
		url:'allowcons/',
		contentType: "application/json",
		success:function(json){
			if(json['status']=='failure'){
				$('#cons').html("No contest requests.");
				return;
			}
			html = "";
			for (data in json){
				pk = json[data].pk
				html+="<div id="+json[data]['pk']+">";
				html += "Name: "+json[data].fields.name+"<br>";
				html += "Code: "+pk+"<br>";
				html += "Start: "+json[data].fields.start_date+"<br>";
				html += "End: "+json[data].fields.end_date+"<br>";
				html += "<button onclick='allow(1, "+pk +")'> Allow </button><button onclick='allow(0, "+pk+")'> Reject </button>";
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
		data: 'ag='+a+"&pk="+pk.id,
		contentType: "application/json",
		success:function(json){
			alert("congratulations.");
		},
		error: function(e){
			alert("Request Failure. Probably because you're not allowed or because of Internet Connection");
		}
	});
}