from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define URLs that don't require authentication
        self.exempt_urls = [
            reverse('login'),
            # Add other URLs that should be publicly accessible
            # For example: reverse('home'), reverse('about'), etc.
        ]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check if the requested path is in exempt URLs
        if request.path in self.exempt_urls:
            return None
        
        # If user is authenticated, allow the request
        if request.user.is_authenticated:
            return None
            
        # Otherwise redirect to login
        return redirect('login')