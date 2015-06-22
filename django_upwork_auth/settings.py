# coding: utf-8

from django.conf import settings


def store_access_token_in_session(token, request):
    request.session[ACCESS_TOKEN_SESSION_KEY] = token


REQUEST_TOKEN_SESSION_KEY = getattr(
    settings, 'UPWORK_OAUTH_REQUEST_TOKEN_SESSION_KEY', '_ort')
u"""OAuth _request token_ will be stored in user's session under this key
during authentication flow. It may make sense to customize this to avoid
clash if your app already uses the default key name for its own purposes."""

ACCESS_TOKEN_STORE_FUNC = getattr(
    settings, 'UPWORK_OAUTH_ACCESS_TOKEN_STORE_FUNC',
    store_access_token_in_session)
u"""This function will be called to store OAuth access token for future access.
It's passed two arguments: a request where user is already
authenticated and the access token associated with that user.
See ``views.OAuthLoginCallback``."""

DEFAULT_ACCESS_TOKEN_SESSION_KEY = '_oat'

ACCESS_TOKEN_SESSION_KEY = getattr(
    settings, 'UPWORK_OAUTH_ACCESS_TOKEN_SESSION_KEY',
    DEFAULT_ACCESS_TOKEN_SESSION_KEY)
u"""OAuth _access token_ will be stored under and retrieved by this
key in user's session, unless you override ACCESS_TOKEN_STORE_FUNC."""

AUTO_CREATE_USERS = getattr(settings, 'UPWORK_AUTH_AUTO_CREATE_USERS', False)

LOGIN_REDIRECT_URL = getattr(
    settings, 'UPWORK_AUTH_LOGIN_REDIRECT_URL',
    settings.LOGIN_REDIRECT_URL)
u"""Where to redirect the user at the end of OAuth flow.
Path or URL pattern name."""


# Access control for stock authentication backend

WHITELIST = getattr(
    settings, 'UPWORK_AUTH_WHITELIST', [])
TEAM_WHITELIST = getattr(
    settings, 'UPWORK_AUTH_TEAM_WHITELIST', [])

STAFF_WHITELIST = getattr(
    settings, 'UPWORK_AUTH_STAFF_WHITELIST', [])
STAFF_TEAM_WHITELIST = getattr(
    settings, 'UPWORK_AUTH_STAFF_TEAM_WHITELIST', [])

SUPERUSER_WHITELIST = getattr(
    settings, 'UPWORK_AUTH_SUPERUSER_WHITELIST', [])
SUPERUSER_TEAM_WHITELIST = getattr(
    settings, 'UPWORK_AUTH_SUPERUSER_TEAM_WHITELIST', [])
