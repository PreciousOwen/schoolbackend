from rest_framework.authentication import SessionAuthentication


class CSRFExemptSessionAuthentication(SessionAuthentication):
    """
    This authentication class will not enforce CSRF validation.
    Use with caution: only do this for API endpoints where you intend to handle authentication differently.
    """

    def enforce_csrf(self, request):
        return  # Simply bypass the csrf check.
