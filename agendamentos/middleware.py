from django.conf import settings
from django.shortcuts import redirect

class HTTPSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Em modo de desenvolvimento, não fazemos redirecionamentos
        if settings.DEBUG:
            return self.get_response(request)

        path = request.path
        
        # Se a URL está na lista de não-HTTPS e está sendo acessada via HTTPS
        if path in settings.NON_HTTPS_URLS and request.is_secure():
            # Força redirecionamento para HTTP
            url = request.build_absolute_uri(request.get_full_path())
            http_url = url.replace('https://', 'http://')
            return redirect(http_url, permanent=True)
            
        # Para todas as outras URLs, mantém HTTPS
        if not request.is_secure() and path not in settings.NON_HTTPS_URLS:
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return redirect(secure_url, permanent=True)
        
        return self.get_response(request) 