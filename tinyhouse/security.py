from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import (
    ACLHelper,
    Authenticated,
    Everyone
)
from pyramid.csrf import CookieCSRFStoragePolicy
from pyramid.request import RequestLocalCache
from pyramid.request import Request

from . import models


class MySecurityPolicy:

    def __init__(self, secret: str):
        self.authtkt = AuthTktCookieHelper(secret)
        self.identity_cache = RequestLocalCache(self.load_identity)
        self.acl = ACLHelper()

    def load_identity(self, request: Request):
        identity = self.authtkt.identify(request)
        if identity is None:
            return None

        userid = identity['userid']
        user = request.dbsession.query(models.User).get(userid)
        return user

    def identity(self, request: Request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request: Request):
        user = self.identity(request)
        if user is not None:
            return user.id

    def remember(self, request: Request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request: Request):
        return self.authtkt.forget(request)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request):
        principals = [Everyone]
        user = self.identity(request)
        if user is not None:
            principals.append(Authenticated)
            principals.append('u:' + str(user.id))
            principals.append('role:' + user.role)

        return principals

def includeme(config):
    settings = config.get_settings()
    config.set_csrf_storage_policy(CookieCSRFStoragePolicy())
    config.set_default_csrf_options(require_csrf=True)
    config.set_security_policy(MySecurityPolicy(settings['auth.secret']))
