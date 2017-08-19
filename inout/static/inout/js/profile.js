$(document).on('click', '#getContests', function() {
	var $contests = $('#contests');

	if ($contests.html()) {
		$('#contestRequests').remove();
	}
	else {
		$.ajax({
			url: "allowcons/",
			type: "GET",
			dataType: "json",
			success: function(contests){
				var $data = contests['contest_requests_html'];

				if(!$data){
					$contests.html("No contest requests.");
					return;
				}

				$contests.html($data);
			}
		});
	}
});

$(document).on('click', '[id^="allow"]', function() {
	const $contest_id = this.id.replace('allow', '');
	allow(this, 1, $contest_id);
});

$(document).on('click', '[id^="reject"]', function() {
	const $contest_id = this.id.replace('reject', '');
	allow(this, 0, $contest_id);
});

const allow = function(elem, is_allowed, contest_code) {
	const data = {
		is_allowed: is_allowed,
		contest_code: contest_code
	};

	$.ajax({
		url: 'allow/',
		type: 'POST',
		data: data,
		dataType: "json",
		success: function(data) {
			if (data.success) {
				var $elem = $('#' + elem.id);
				$elem.parent().html('Successfully applied.');
			}
		},
		error: function(e){
			alert("Request Failure. Probably because you're not allowed or because of Internet Connection");
		}
	});
}