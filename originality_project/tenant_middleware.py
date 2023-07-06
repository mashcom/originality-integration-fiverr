from django.shortcuts import redirect
from tenant_management.models import UserTenant
from django.shortcuts import render, HttpResponse, redirect

class TenantMiddleware:
    EXCLUDED_URLS = [
        '/accounts/logout/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Check if the current URL is in the excluded URLs list
        if request.path_info in self.EXCLUDED_URLS:
            return self.get_response(request)
        # Check if the user is logged in
        if request.user.is_authenticated:
            try:
                # Retrieve the tenant_id from the UserTenant model
                user_tenant = UserTenant.objects.get(user_id=request.user.id)
                tenant_id = user_tenant.tenant_id
            except UserTenant.DoesNotExist:
                # Redirect the user to a page indicating the absence of tenant information
                return render(request,'no_tenant_page.html')  # Adjust the URL or view name as needed

            # Set the tenant_id in the request's session for future use
            request.session['tenant_id'] = tenant_id

        response = self.get_response(request)
        return response
