# coding: utf-8

import mock
import urllib2

import upwork

from django.test import TestCase

from . import utils


class LoginCheckTestCase(TestCase):

    @mock.patch('django_upwork_auth.utils.get_client')
    def test_http_error(self, client_getter):
        client = client_getter.return_value
        client.hr.get_user.side_effect = urllib2.HTTPError(
            '/fake-url',
            503,
            'Service Unavailable',
            {},  # headers
            None,  # fp
        )

        result = utils.check_login(('dummy', 'dummy'))

        self.assertTrue(client_getter.called)
        self.assertEqual(result, (False, "Network error"))

    @mock.patch('django_upwork_auth.utils.get_client')
    def test_url_error(self, client_getter):
        client = client_getter.return_value
        client.hr.get_user.side_effect = urllib2.URLError(
            'connection reset by peer')

        result = utils.check_login(('dummy', 'dummy'))

        self.assertTrue(client_getter.called)
        self.assertEqual(result, (False, "Network error"))

    @mock.patch('django_upwork_auth.utils.get_client')
    def test_invalid_token(self, client_getter):
        client = client_getter.return_value
        client.hr.get_user.side_effect = (
            upwork.exceptions.HTTP403ForbiddenError(
                '/fake-url',
                403,
                'Forbidden',
                {},  # headers
                None,  # fp
            )
        )

        result = utils.check_login(('dummy', 'dummy'))

        self.assertTrue(client_getter.called)
        self.assertEqual(result, (False, "Invalid access token"))

    @mock.patch('django_upwork_auth.utils.get_client')
    def test_inactive_user(self, client_getter):
        client = client_getter.return_value
        client.hr.get_user.return_value = {
            'status': 'bad status',
            'first_name': 'name',
            'last_name': 'surname',
            'uid': 'userid',
            'mail': 'user@example.net',
        }

        result = utils.check_login(('dummy', 'dummy'))

        self.assertTrue(client_getter.called)
        self.assertEqual(result, (False, "User is inactive"))

    @mock.patch('django_upwork_auth.utils.get_client')
    def test_ok(self, client_getter):
        client = client_getter.return_value
        client.hr.get_user.return_value = {
            'status': 'active',
            'first_name': 'name',
            'last_name': 'surname',
            'uid': 'userid',
            'mail': 'user@example.net',
        }

        result = utils.check_login(('dummy', 'dummy'))

        self.assertTrue(client_getter.called)
        self.assertEqual(result, (True, "OK"))
