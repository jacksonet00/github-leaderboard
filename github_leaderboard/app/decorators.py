from django.core.exceptions import PermissionDenied

"""
Plese apply 'login_required' decorator before these decorators to ensure that
request.user won't be AnonymousUser. Otherwise, it will cause exception
"""


def admin_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.role == "ADMIN":
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not authorized.")

    wrap.__doc__ = function.__doc__
    return wrap


def dev_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.role == "DEV":
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not authorized.")

    wrap.__doc__ = function.__doc__
    return wrap


def admin_or_dev_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.role == "ADMIN" or request.user.role == "DEV":
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not authorized.")

    wrap.__doc__ = function.__doc__
    return wrap
