# coding: utf-8

import logging
import urllib2

from upwork import Client as UpworkClient
from upwork import exceptions as upwork_exceptions

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site


log = logging.getLogger(__name__)


def get_client(access_token=None):
    u"""Returns python-upwork Client instance with OAuth key set
    and optionally pre-filled access token."""

    try:
        key = settings.UPWORK_OAUTH_KEY
        secret = settings.UPWORK_OAUTH_SECRET
    except AttributeError:
        raise ImproperlyConfigured(
            "UPWORK_OAUTH_KEY and/or UPWORK_OAUTH_SECRET settings missing")

    client = UpworkClient(key, secret)

    if access_token:
        (
            client.oauth_access_token,
            client.oauth_access_token_secret,
        ) = access_token

    return client


def check_login(access_token):
    u"""Verifies that given OAuth ``access_token`` is valid and Upwork says
    user has active status. Makes a test request to Upwork API for that purpose.

    Returns a 2-tuple. If login is bad, it's ``False`` and a string with
    additional information. Otherwise it's ``(True, "OK")``."""

    upwork_client = get_client(access_token)

    try:
        upwork_user_data = upwork_client.hr.get_user('me')

    except upwork_exceptions.HTTP403ForbiddenError:
        return False, "Invalid access token"

    except (urllib2.HTTPError, urllib2.URLError):
        log.exception(u"Unexpected network error in check_login()")
        return False, "Network error"

    except ValueError as exc:
        log.exception(exc)
        return False, "Value error"

    if upwork_user_data.get('status') != 'active':
        return False, "User is inactive"

    return True, "OK"


def get_host(request):
    return Site.objects.get_current()
