from django.middleware.csrf import _get_new_csrf_token


def issue_new_csrf_token(request):
    """
    csrf token is used after registration
    new token is issued in request for activation form
    """

    request.META["CSRF_COOKIE"] = _get_new_csrf_token()
    request.META['CSRF_COOKIE_USED'] = False

    return request
