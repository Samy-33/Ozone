//function add(code){
//	$.ajax({
//		url:"contests/q/"+code+"/a/",
//		type:"POST",
//		
//	});
//}

function getTests(){
	
	var n = document.getElementById('id_n_testfiles').value;
	document.getElementsByTagName("form")[0].setAttribute('enctype', "multipart/form-data");
	var tests = document.getElementById("tests");
	for(var i = 0; i < n; i++){
		var inp = document.createElement('input');
		var out = document.createElement('input');
		inp.name = "in"+i+".txt";
		out.name ="out"+i+".txt";
		inp.required = out.required = true;
		inp.type = out.type = 'file';
		
		tests.innerHTML += "<tr><td>";
		tests.appendChild(inp);
		tests.innerHTML += "</td>";
		tests.appendChild(out);
		tests.innerHTML += "</td></tr>";
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
