import time
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware as BaseSessionMiddleware
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.backends.base import UpdateError
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date

ADMIN_SESSION_COOKIE_NAME = 'admin_sessionid'


class DualSessionMiddleware(BaseSessionMiddleware):
    """
    Gives the admin panel (/admin/) its own session cookie, completely separate
    from the customer-facing site's session cookie.

    Why: by default Django uses ONE session cookie for the whole site, so logging
    out anywhere (e.g. a customer clicking "Logout") destroys the session for
    EVERYONE using that browser — including an admin who is logged into /admin/
    in another tab. This middleware fixes that by using two independent cookies,
    so an admin login and a customer login can coexist in the same browser, and
    logging out of one never logs out the other.
    """

    def _cookie_name(self, request):
        if request.path.startswith('/admin/'):
            return ADMIN_SESSION_COOKIE_NAME
        return settings.SESSION_COOKIE_NAME

    def process_request(self, request):
        cookie_name = self._cookie_name(request)
        session_key = request.COOKIES.get(cookie_name)
        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response

        cookie_name = self._cookie_name(request)

        if cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                cookie_name,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                if response.status_code != 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SuspiciousOperation(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )
                    response.set_cookie(
                        cookie_name,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
        return response
