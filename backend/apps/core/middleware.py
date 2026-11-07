from contextvars import ContextVar

_current_user = ContextVar("current_audit_user", default=None)
_current_ip = ContextVar("current_audit_ip", default=None)


def get_current_user():
    return _current_user.get()


def get_current_ip():
    return _current_ip.get()


class AuditUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        ip_address = request.META.get("REMOTE_ADDR")

        user_token = _current_user.set(user)
        ip_token = _current_ip.set(ip_address)

        try:
            response = self.get_response(request)
        finally:
            _current_user.reset(user_token)
            _current_ip.reset(ip_token)

        return response
