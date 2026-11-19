from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):

    target_class = "apps.accounts.authentication.CookieJWTAuthentication"

    name = "CookieJWT"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "voyavisa_access",
        }