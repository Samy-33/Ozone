/* Javascript utilities for authentication */

$(document).ready(function() {
  $('.navigation-bar').css('display', 'none');
});

$(document).on('click', '#registerBtn', function(e) {
    e.preventDefault();

    $('#login').addClass('hide');
    $('#activate').addClass('hide');
    $('#register').removeClass('hide');
});

$(document).on('click', '#loginBtn', function(e) {
    e.preventDefault();

    $('#login').removeClass('hide');
    $('#activate').addClass('hide');
    $('#register').addClass('hide');
});

$(document).on('click', '#activateBtn', function(e) {
    e.preventDefault();

    $('#login').addClass('hide');
    $('#activate').removeClass('hide');
    $('#register').addClass('hide');
});

getErrorHtml = function(message) {
    var errorList = '<ul>';
    
    for (var i=0; i < message.length; i++) {
        errorList += '<li>' + message[i] + '</li>';
    }
    
    errorList += '</ul>';
    return errorList;
}

$(document).on('click', '#submitLogin', function(e) {
    e.preventDefault();

    var data = {
        username: $('#lusername').val(),
        password: $('#lpassword').val(),
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]')[0].value
    }

    if (!data.username || !data.password) {
        return;
    }

    $.ajax({
        url: '/authenticate/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function(data) {
            if (!data.success) {
                var $message = data.message,
                    $errors = getErrorHtml($message);

                $('#login-errors').html($errors);
                $('#login-errors').removeClass('hide');
            }
            else {
                window.location.href = '/home/';
            }
        }
    });
});

$(document).on('click', '#submitRegister', function(e) {
    e.preventDefault();

    var data = {
        username: $('#rusername').val(),
        fname: $('#rfname').val(),
        lname: $('#rlname').val(),
        dob: $('#rdob').val(),
        password1: $('#rpassword1').val(),
        password2: $('#rpassword2').val(),
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]')[0].value
    }

    if (!data.username || !data.fname || !data.lname || !data.password1 || !data.password2) {
        return;
    }

    $.ajax({
        url: '/register/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function(data) {
            if (!data.success) {
                var $message = data.message,
                    $errors = getErrorHtml($message);

                $('#register-errors').html($errors);
                $('#register-errors').removeClass('hide');
                $('#rpassword1').val('');
                $('#rpassword2').val('');
            }
            else {
                $('#activateBtn').click();
            }
        }
    });
});
