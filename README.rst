django-upwork-auth
==================

Simple Upwork login for your Django-based project.

Note: at current version it has inflexible and impossible to disable access control.
It suits my own needs so far but I plan to improve on this, given demand.

Tested with Django 1.8 (see example project).

Before oDesk rebranded as Upwork, this library was called django-odesk-auth.
The latest version of django-odesk-auth works with Upwork already.
This library is not backwards compatible with django-odesk-auth.


Creating Upwork OAuth API key
----------------------------

Go to https://www.upwork.com/services/api/apply.

* Authentication type should be set to "OAuth 1.0".
* Callback URL should be left blank.
* Default authentication backend requires
  "View the structure of your companies/teams" permission to be checked.


Adding Upwork auth to your Django project
-----------------------------------------

Make sure you have ``django-upwork-auth`` and ``python-upwork==1.0`` installed.
Make sure you have Django's sites and session frameworks enabled.

1. Add ``'django_upwork_auth'`` to ``INSTALLED_APPS``.

2. Add ``'django_upwork_auth.backends.UpworkOAuthBackend'``
   to AUTHENTICATION_BACKENDS.

3. Specify ``UPWORK_OAUTH_KEY`` and ``UPWORK_OAUTH_SECRET`` settings
   with your key information.

4. Add ``'your_upwork_username'`` to ``UPWORK_AUTH_ALLOWED_USERS``,
   and set ``UPWORK_AUTH_AUTO_CREATE_USERS`` to True.

5. Include ``django_upwork_auth.urls`` in your URL patterns.

6. In your login page template, put a link (say, "Log in via Upwork")
   and point it to ``{% url "upwork_oauth_login" %}``.

7. Open login page and click "Log in via Upwork" to verify everything works.

IMPORTANT: keep ``UPWORK_OAUTH_KEY`` and ``UPWORK_OAUTH_SECRET`` settings
in a file that is not under version control. One way to do that is to keep
all public settings in versioned file named say ``settings_base.py``,
from which you import everything in ``settings.py`` that is not versioned.
Django in this setup should be pointed to ``settings.py``, as usual.


Example project
---------------

Requirements: Vagrant, Ansible, and free 8000 port.

First, fill in the necessary settings in ``example_project/settings.py``
(see comments in the file).

From ``example_project`` directory, bring up a VM using Vagrantfile provided
and manually run Django development server in it::

    $ vagrant up
    $ vagrant ssh
    vm$ cd /vagrant/example_project/
    vm$ ./manage.py runserver 0.0.0.0:8000

On your host machine, navigate to 127.0.0.1:8000 where you should be able
to test Upwork login functionality in action.


Authentication backend
----------------------

Stock authentication backend assumes that you only use Upwork login in your app.
When someone logs in, if their Upwork ID matches existing username, it logs
them in as that user. If there's no username matching given Upwork ID, it optionally
creates a user with such username.

ATTENTION: Watch out you are using other authentication methods
or for some reason have any chance of one end user's Upwork ID matching
existing username of another end user!

Stock authentication backend provides optional basic access control facilities.
You can specify who is allowed to log in to your site and who upon login gets
staff and/or superuser statuses. This is configured through Django settings.

If whitelisting is on and given user is not on the white list, their
``User.is_active`` flag gets set to False upon login.

See below for settings provided by stock authentication backend.

You can subclass stock authentication backend to override user manipulation
(see ``handle_unknown_user()`` and ``update_user()`` methods).


Making authenticated Upwork API calls
-------------------------------------

After user is successfully authenticated you can call Upwork API on their behalf.
For that you'd need the access token obtained during OAuth flow.

By default this app uses Django's built-in session framework to store
access token. The key it uses can be retrieved from
``django_upwork_auth.settings.ACCESS_TOKEN_SESSION_KEY``
and customized via ``UPWORK_OAUTH_ACCESS_TOKEN_SESSION_KEY`` setting.

Example code you can have in your view::

    from django_upwork_auth import utils, settings

    upwork_client = utils.get_client(
        request.session[settings.ACCESS_TOKEN_SESSION_KEY])

    print upwork_client.hr.get_teams()
    # Should output list of teamrooms current user belongs to

You can use another storage technique by overriding
``UPWORK_OAUTH_ACCESS_TOKEN_STORE_FUNC``. It's useful if you need to make Upwork API call
but can't easily read user's session because there's no request context.
For example, you can store access token with associated username in Redis
and query it in your asynchronous tasks.

Note:

* How you make API calls is up to you. Internally django-upwork-auth
  uses python-upwork library, and so does the above example.

* ``utils.get_client()`` function returns an instance of ``upwork.Client``.
  Handy if you're using python-upwork library to make API calls.


Verifying OAuth access token
----------------------------

Sometimes there's a need to make sure that current user's authentication
is still valid—that they, for example, didn't revoke access to their account.

This app provides a helper for that: see ``utils.check_login()``.
It can be used in a view like this::

    from django_upwork_auth import utils

    def oauth_check_login(request):
        u"""Verifies OAuth access token and user status on Upwork.
        Returns HTTP 200 (OK) or HTTP 401 (Unauthorized)
        with additional information in response body text.
        """
        access_token = utils.access_token.get(request)
 
        if access_token is None or len(access_token) != 2:
            return http.HttpResponse(
                u"Bad or missing Upwork OAuth access token", status=401)
 
        result, details = utils.check_login(access_token)
 
        if result is True:
            return http.HttpResponse(details, status=200)
        else:
            return http.HttpResponse(details, status=401)


Available Django settings
-------------------------

UPWORK_OAUTH_KEY, UPWORK_OAUTH_SECRET
  API key information.

UPWORK_AUTH_LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
  Where to redirect the user at the end of OAuth flow.
  Path or URL pattern name.

UPWORK_AUTH_ACCESS_TOKEN_STORE_FUNC
  Function to be called to store OAuth access token for future access.
  It's passed two arguments: a request where user is already
  authenticated and the access token associated with that user.
  Default implementation stores token in session under ``ACCESS_TOKEN_SESSION_KEY``.


Specific to stock authentication backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are relevant unless you subclass stock ``backends.UpworkOAuthBackend`` and override
some of its logic.

By default anyone can log in, given Upwork returns "active" as their account status.
Whitelist mode can be turned on by filling ``UPWORK_AUTH_WHITELISTED_USERS`` and/or
``UPWORK_AUTH_WHITELISTED_TEAMS``.

UPWORK_AUTH_AUTO_CREATE_USERS = False
  Whether to create a new account in Django if given user uses Upwork login
  for the first time (i.e., ID returned by Upwork is free in your Django DB).

UPWORK_AUTH_WHITELIST = ()  
  Upwork IDs of users who are allowed to log in via Upwork.

UPWORK_AUTH_STAFF_WHITELIST = ()  
  Upwork IDs of users who are marked as ``is_staff`` upon login.

UPWORK_AUTH_SUPERUSER_WHITELIST = ()  
  Upwork IDs of users who are marked as ``is_superuser`` upon login.

UPWORK_AUTH_TEAM_WHITELIST = ()  
  IDs of Upwork teamrooms, members of which are allowed to log in via Upwork.

UPWORK_AUTH_STAFF_TEAM_WHITELIST = ()  
  IDs of Upwork teamrooms, members of which are marked as ``is_staff`` upon login.

UPWORK_AUTH_SUPERUSER_TEAM_WHITELIST = ()  
  IDs of Upwork teamrooms, members of which are marked as ``is_superuser`` upon login.
