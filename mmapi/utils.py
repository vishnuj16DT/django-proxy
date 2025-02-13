from django.test.client import RequestFactory

def modify_request_headers(request, new_headers):
    """Create a new request object with modified headers"""
    factory = RequestFactory()
    
    # Create a new request with the same method, path, and headers
    new_request = factory.generic(
        request.method,
        request.path,
        data=request.body,  # Preserve body
        content_type=request.content_type
    )

    # Copy old headers and update with new headers
    new_request.META.update(request.META)
    for key, value in new_headers.items():
        new_request.META[f"HTTP_{key.upper().replace('-', '_')}"] = value

    return new_request
