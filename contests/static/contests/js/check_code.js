function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});



function submit(problem){
	var code = document.getElementById("editcode").value;
	var lang = document.getElementById("lang").value;

	$.ajax({
		type:'POST',
		url: '/contests/q/submit/'+problem+"/",
		data:{'code':code, 'lang':lang},
		beforeSend: function(xhr, settings){
			console.log("Before send");
			$.ajaxSettings.beforeSend(xhr, settings);
		},
		success:function(data){
			document.getElementById("result").innerHTML = data;
			console.log(data)
		}
	});
}