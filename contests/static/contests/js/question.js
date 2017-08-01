function checkForm(){
//    alert(parseInt($('#id_n_testfiles').val()) <= 0);
    if($('#id_code').val() == '' || $('#id_name').val() == '') return false;
    return !(parseInt($('#id_n_testfiles').val()) <= 0);
}

function getTests(){
    if(!checkForm()){
        $('#error').css('display', 'inherit');
        $('#error').html(" Enter Correct data <ul><li> Can't leave blank <li> Number of testcases must be more than 0. </ul>");
        return;
    }
    $("#error").css('display', 'None'); 
    $('#tests').html('');
    var n = parseInt(document.getElementById('id_n_testfiles').value);
    document.getElementsByTagName("form")[0].setAttribute('enctype', "multipart/form-data");
    var tests = document.getElementById("tests");
    for(var i = 0; i < n; i++){
        html = "<tr><td> Input "+i+": </td><td><input name=in"+i+".txt required type=file /></td><td> Output "+i+": </td><td><input name=out"+i+".txt required type=file /></td></tr>";
        $('#tests').append(html);
    }
    var button = document.getElementById("sbmt");
    button.setAttribute('type', 'submit');
    button.removeAttribute("onclick");
    button.setAttribute("form", "addq");
    button.value="submit";
    button.innerHTML = "Submit";
}

$(document).ready(function(){
   $("#error").css('display', 'None');
});