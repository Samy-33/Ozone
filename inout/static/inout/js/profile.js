$(document).on('click', '#get_contests', function() {
	$.ajax({
		url: "allowcons/",
		type: "GET",
		dataType: "json",
		success: function(contests){
			var $contests = $('#contests');

			if(contests['status'] === 'failure'){
				$contests.html("No contest requests.");
				return;
			}

			contests_html = "";
			for (contest in contests){
				var pk = contests[contest].pk,
					name = contests[contest].fields.name,
					start_date = contests[contest].fields.start_date,
					end_date = contests[contest].fields.end_date;

				contests_html += "<div id=" + pk + ">";
				contests_html += "Name: " + name + "<br>";
				contests_html += "Code: " + pk + "<br>";
				contests_html += "Start: " + start_date + "<br>";
				contests_html += "End: " + end_date + "<br>";
				contests_html += "<button onclick='allow(1, " + pk +")'> Allow </button><button onclick='allow(0, "+ pk +")'> Reject </button>";
				contests_html += "</div>";
			}
			$contests.html(contests_html);
		},
		error: function(e){
			$contests.html("No contest requests.");
		}
	});
});


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