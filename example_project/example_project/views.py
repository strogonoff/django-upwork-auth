from django import http
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.conf import settings

from django_upwork_auth.settings import ACCESS_TOKEN_SESSION_KEY


class GuestView(TemplateView):
    template_name = 'guest.html'

    def get_context_data(self, **kwargs):
        return dict(
            configured=all([
                hasattr(settings, 'UPWORK_OAUTH_KEY'),
                hasattr(settings, 'UPWORK_OAUTH_SECRET'),
            ]),
        )


class MemberView(TemplateView):
    template_name = 'member.html'

    def get_context_data(self, **kwargs):
        return dict(
            token=self.request.session.get(ACCESS_TOKEN_SESSION_KEY)[0],
        )

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect(reverse('guest_page'))

        return super(MemberView, self).get(request, *args, **kwargs)
