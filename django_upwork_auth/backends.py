# coding: utf-8

import logging

from upwork import exceptions as upwork_exceptions

from django.contrib.auth.models import User

from . import utils
from . import settings


logger = logging.getLogger(__name__)


class UpworkOAuthBackend(object):
    u"""Upwork OAuth backend for Django auth system."""

    def authenticate(self, access_token=None):
        u"""Verifies that given OAuth ``access_token`` is valid by making
        a request to Upwork API fetching current user's information.

        Looks for existing User object with username user's Upwork ID.
        Assumes that found User object represents our user.
        Updates User object attributes based on information
        received from Upwork.

        ATTENTION: Watch out you are using other authentication methods
        or for some reason have any chance of Upwork ID matching
        existing username of another user.

        If fetched Upwork ID doesn't have a match, optionally creates
        user with given Upwork ID."""

        self.upwork_client = utils.get_client(access_token)

        try:
            upwork_user_data = self.upwork_client.hr.get_user('me')
            # Upwork user information is expected to contain at least
            # user's ID, first name, last name, email, and status.

        except upwork_exceptions.HTTP403ForbiddenError:
            logger.warn(
                u"Possibly bad Upwork OAuth access token. "
                u"Got Forbidden during login flow.")
            return None

        user = (self.match_existing_user(upwork_user_data)
                or self.handle_unknown_user(upwork_user_data))

        if user:
            self.update_user(user, upwork_user_data)

        return user

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def match_existing_user(self, upwork_user_data):
        u"""Decides which User to log our incoming in as.
        Returns User or None."""

        try:
            return User.objects.get(username=upwork_user_data['id'])
        except User.DoesNotExist:
            return None

    def handle_unknown_user(self, upwork_user_data):
        u"""Called when a user trying Upwork login is not found in the system.
        Returns User object or None.

        Default implementation optionally creates new user
        based on flag in settings."""

        if settings.AUTO_CREATE_USERS:
            return User.objects.get_or_create(username=upwork_user_data['id'])
        else:
            return None

    def update_user(self, user, upwork_user_data):
        u"""Sets properties on given freshly authenticated ``User`` instance
        based on provided Upwork data dictionary at OAuth flow end.

        Default implementation updates some user details and sets appropriate
        access control flags based on whitelists."""

        # User details
        user.first_name = upwork_user_data['first_name']
        user.last_name = upwork_user_data['last_name']
        user.email = upwork_user_data['email']

        # Basic whitelist functionality
        whitelist_enabled = any([
            len(settings.WHITELIST) > 0,
            len(settings.TEAM_WHITELIST) > 0])

        teams = set(team['id'] for team in self.upwork_client.hr.get_teams())

        user.is_active = (upwork_user_data.get('status') == 'active') and any([
            not whitelist_enabled,
            user.is_staff,
            user.is_superuser,
            user.username in settings.WHITELIST,
            teams & set(settings.TEAM_WHITELIST),
        ])

        # Assigning is_staff and is_superuser flags
        user.is_staff = any([
            user.username in settings.STAFF_WHITELIST,
            teams & set(settings.STAFF_TEAM_WHITELIST),
        ])

        user.is_superuser = any([
            user.username in settings.SUPERUSER_WHITELIST,
            teams & set(settings.SUPERUSER_TEAM_WHITELIST),
        ])

        user.save()
