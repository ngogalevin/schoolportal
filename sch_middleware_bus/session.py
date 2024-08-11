import logging
from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

# Set up a logger
logger = logging.getLogger(__name__)

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self.is_admin_url(request) and not request.user.is_superuser:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')
           
            if last_activity:
                inactive_time = (current_time - last_activity).total_seconds()
                if inactive_time > settings.SESSION_COOKIE_AGE:
                    # Log the session expiry
                    logger.info(
                        f"User {request.user.username} (ID: {request.user.id}) logged out due to "
                        f"session expiry. Inactive for {inactive_time:.2f} seconds. "
                        f"IP: {self.get_client_ip(request)}"
                    )
                    logout(request)
                    return redirect('login')  # Adjust 'login' to your login URL name
           
            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response

    def is_admin_url(self, request):
        resolved = resolve(request.path_info)
        return resolved.app_name == 'admin' or resolved.namespace == 'admin'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip



class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/auth/' and request.user.is_authenticated:
            return redirect('contact')
        return self.get_response(request)
