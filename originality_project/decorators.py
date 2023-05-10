from django.http import Http404
from django.core.exceptions import PermissionDenied

from .constants import Group
from django.contrib.auth.models import User

def check_user_able_to_see_page(*groups: Group):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            # print(request.u)
            if request.user.groups.filter(
                    name__in=[group for group in groups]
            ).exists():
                return function(request, *args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator
