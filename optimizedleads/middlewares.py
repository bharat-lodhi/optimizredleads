from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedAccessMiddleware:
    """
    Middleware to restrict access to certain URL paths based on user role.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Only check for these paths
        protected_paths = {
            'central-admin': 'central_admin',
            'sub-admin': 'sub_admin',
            'subscribers': 'subscriber',
        }

        for url_start, required_role in protected_paths.items():
            if path.startswith(f'/{url_start}'):
                user = getattr(request, 'user', None)
                # If user not authenticated or role mismatch
                if not user or not user.is_authenticated or getattr(user, 'role', None) != required_role:
                    return redirect('/login/') # Assuming login URL is landing:login

        response = self.get_response(request)
        return response
