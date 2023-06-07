from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import PermissionDenied, BadRequest

from .constants import Group

def check_user_able_to_see_page(*groups: Group):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(
                    name__in=[group for group in groups]
            ).exists() or request.user.is_superuser:
                return function(request, *args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator

def google_authentication_required():
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            try:
                SocialAccount.objects.filter(user=request.user)[0].uid
                return function(request, *args, **kwargs)
            except IndexError:
                raise BadRequest

        return wrapper

    return decorator
