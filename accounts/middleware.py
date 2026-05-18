from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Redirige les utilisateurs qui doivent changer leur mot de passe."""
    EXEMPT_URLS = ['/accounts/profil/', '/accounts/logout/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and
                getattr(request.user, 'must_change_password', False) and
                request.path not in self.EXEMPT_URLS):
            return redirect(reverse('accounts:profil') + '?force_pwd=1')
        return self.get_response(request)
