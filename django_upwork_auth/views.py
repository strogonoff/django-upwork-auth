# coding: utf-8

import logging

from django import http
from django.views.generic.base import View
from django.shortcuts import resolve_url
from django.contrib.auth import authenticate, login
from django.utils.http import is_safe_url

from . import utils
from . import settings


log = logging.getLogger(__name__)


def oauth_login(request):
    u"""Initiates OAuth flow.

    Obtains request token and redirects user to Upwork side.
    Upwork is asked to redirect user to URL resolved from pattern named
    'upwork_oauth_login_callback'.

    Passes along GET parameter named "next", which specifies
    where user should be redirected after OAuth login callback is handled."""

    client = utils.get_client()

    request.session[settings.REQUEST_TOKEN_SESSION_KEY] = (
        client.auth.get_request_token())

    return http.HttpResponseRedirect(client.auth.get_authorize_url(
        'http://{host}{path}?next={success_redirect}'.format(
            host=utils.get_host(request),
            path=resolve_url('upwork_oauth_login_callback'),
            success_redirect=request.GET.get('next'),
        )
    ))


class OAuthLoginCallback(View):
    u"""Handles redirect from Upwork side during OAuth login flow.

    Fetches request token obtained on previous step. Request token
    and verifier passed from Upwork are used to obtain access token.
    Access token is passed to authentication backend as credentials.

    In case of success, redirects to path under "next" GET parameter."""

    def dispatch(self, *args, **kwargs):
        self.client = utils.get_client()
        return super(OAuthLoginCallback, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        (
            self.client.auth.request_token,
            self.client.auth.request_token_secret,
        ) = self.pop_request_token()

        verifier = self.request.GET.get('oauth_verifier')
        access_token = self.client.auth.get_access_token(verifier)

        # Delegate a bunch of work to provided Upwork authentication backend
        user = authenticate(access_token=access_token)

        if user:
            # Store access token for future use
            settings.ACCESS_TOKEN_STORE_FUNC(access_token, request)

            login(request, user)
            return self.handle_authentication_success(user)

        return self.handle_authentication_failure()

    def pop_request_token(self):
        try:
            token = self.request.session[settings.REQUEST_TOKEN_SESSION_KEY]
        except KeyError:
            log.error(u"No OAuth request token found in session")
            raise
        else:
            del self.request.session[settings.REQUEST_TOKEN_SESSION_KEY]

        return token

    def handle_authentication_failure(self):
        return http.HttpResponse(u"User not found", status=401)

    def handle_authentication_success(self, user):
        return http.HttpResponseRedirect(self.get_redirect_url())

    def get_redirect_url(self):
        redirect_to = self.request.GET.get('next')

        if any([redirect_to is None,
                redirect_to == 'None',  # Upwork quirk
                not is_safe_url(redirect_to, host=self.request.get_host())]):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to
