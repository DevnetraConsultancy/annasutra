"""Security headers middleware for AnnaSutra complying with OWASP ASVS 5.0 and docs/07."""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Injects strict security headers into all HTTP responses.
    
    Headers enforced:
    - Content-Security-Policy (CSP)
    - Permissions-Policy
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - Referrer-Policy: strict-origin-when-cross-origin
    - Cache-Control for sensitive API endpoints
    """

    def process_request(self, request):
        if getattr(settings, "DEBUG", False) and request.method == "OPTIONS":
            from django.http import HttpResponse
            response = HttpResponse()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Idempotency-Key"
            return response
        return None

    def process_response(self, request, response):
        if getattr(settings, "DEBUG", False):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Idempotency-Key"

        # 1. Content Security Policy: strict origin, no unsafe-inline scripts
        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 2. Permissions Policy (disable high-risk APIs, restrict camera to self)
        permissions_directives = [
            "geolocation=()",
            "microphone=()",
            "camera=(self)",
            "payment=()",
            "usb=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        # 3. Standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Prevent caching on sensitive API and auth routes
        if request.path.startswith("/v1/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        # 5. Strict-Transport-Security (HSTS) when on HTTPS
        if request.is_secure() or getattr(settings, "SECURE_HSTS_SECONDS", 0) > 0:
            hsts_val = f"max-age={getattr(settings, 'SECURE_HSTS_SECONDS', 31536000)}; includeSubDomains; preload"
            response.headers["Strict-Transport-Security"] = hsts_val

        return response
