class SubdomainMiddleware:
    """Middleware to detect and process subdomains."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        domain_parts = host.split('.')
        path = request.path_info.lstrip('/')
        
        # Skip subdomain processing for business/ and api/ paths
        if path.startswith('business/') or path.startswith('api/') or path.startswith('admin/'):
            request.subdomain = None
            return self.get_response(request)
        
        # Check if accessing a subdomain
        if len(domain_parts) > 2 and domain_parts[0] != 'www':
            request.subdomain = domain_parts[0]
        # For local development, handle localhost:8000 format
        elif len(domain_parts) == 1 and '.' not in domain_parts[0]:
            # This means we're on localhost, extract subdomain from first path component
            path_parts = path.split('/')
            # Use the first path component as our subdomain if it exists
            request.subdomain = path_parts[0] if path_parts and path_parts[0] else None
            # Rewrite the path to remove the subdomain component
            if request.subdomain:
                request.path_info = '/' + '/'.join(path_parts[1:])
        else:
            request.subdomain = None
            
        return self.get_response(request)