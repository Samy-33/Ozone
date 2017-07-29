/* Javascript utilities for authentication */

$(document).ready(function() {
  $('.navigation-bar').css('display', 'none');
});

$(document).on('click', '#registerBtn', function(e) {
    e.preventDefault();

    window.history.pushState({}, null, '?showSection=register');

    $('#login').addClass('hide');
    $('#activate').addClass('hide');
    $('#register').removeClass('hide');
    $('#formErrors').addClass('hide');
    removeRedBorder();
});

$(document).on('click', '#loginBtn', function(e) {
    e.preventDefault();

    window.history.pushState({}, null, '?showSection=login');

    $('#login').removeClass('hide');
    $('#activate').addClass('hide');
    $('#register').addClass('hide');
    $('#formErrors').addClass('hide');
    removeRedBorder();
});

removeRedBorder = function() {
    var elements = $('.red-border');
    for (var i=0; i < elements.length; i++) {
        elements[i].classList.remove('red-border');
    }
}

getErrorHtml = function(message) {
    var errorList = '<ul>';
    
    for (var i=0; i < message.length; i++) {
        errorList += '<li>' + message[i] + '</li>';
    }
    
    errorList += '</ul>';
    return errorList;
}

validateRequiredFields = function() {
    var is_valid = true;
    for (var i=0; i < arguments.length; i++) {
        if (!arguments[i].val()) {
            $('#formErrors').removeClass('hide');
            arguments[i].addClass('red-border');
            is_valid = false;
        }
        else {
            arguments[i].removeClass('red-border');
        }
    }

    if (is_valid) {
        $('#formErrors').addClass('hide');
    }

    return is_valid;
}

$(document).on('click', '#submitLogin', function(e) {
    e.preventDefault();

    var $username = $('#lusername'),
        $password = $('#lpassword');

    validateRequiredFields($username, $password);

    var data = {
        username: $username.val(),
        password: $password.val(),
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]')[0].value
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

                $('#formErrors').children('ul').html($errors);
                $('#formErrors').removeClass('hide');
            }
            else {
                $('#formErrors').addClass('hide');

                if (data.is_activated) {
                    window.location.href = '/home/';
                }
                else {
                    $('#activate').removeClass('hide');
                    $('#login').addClass('hide');
                    window.history.pushState({}, null, '?showSection=activate');
                }
            }
        }
    });
});

$(document).on('click', '#submitRegister', function(e) {
    e.preventDefault();

    var $username = $('#rusername'),
        $fname = $('#rfname'),
        $lname = $('#rlname'),
        $dob = $('#rdob'),
        $password1 = $('#rpassword1'),
        $password2 = $('#rpassword2');

    var data = {
        username: $username.val(),
        fname: $fname.val(),
        lname: $lname.val(),
        dob: $dob.val(),
        password1: $password1.val(),
        password2: $password2.val(),
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]')[0].value
    }

    validateRequiredFields($username, $fname, $lname, $password1, $password2);

    $.ajax({
        url: '/register/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function(data) {
            if (!data.success) {
                var $message = data.message,
                    $errors = getErrorHtml($message);

                $('#formErrors').children('ul').html($errors);
                $('#formErrors').removeClass('hide');
                $('#rpassword1').val('');
                $('#rpassword2').val('');
            }
            else {
                $('#formErrors').addClass('hide');
                $('#activate').removeClass('hide');
                $('#register').addClass('hide');
                window.history.pushState({}, null, '?showSection=activate');
            }
        }
    });
});
