
function getCon(){
//	alert("hel");
	$.ajax({
		url:'allowcons/',
		contentType: "application/json",
		success:function(json){
//			alert("hell");
			html = "wow";
			for (var v in json){
				html += "<p>"+json[v]+"</p>";
			}
			$('#cons').html(html);
		},
		error: function(e){
			$('#cons').html("No contest requests.");
		}
	});
}