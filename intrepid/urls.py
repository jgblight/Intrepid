from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
import django.contrib.auth
from django.conf import settings
from django.conf.urls.static import static
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from intrepid_app.api import ActiveTripHandler

from django.conf import settings
from django.http import HttpResponseRedirect

def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

auth = HttpBasicAuthentication(realm="Intrepid")
ad = { 'authentication': auth }

active_trip_resource = secure_required(Resource(handler=ActiveTripHandler,**ad))

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
	url(r'^login$','django.contrib.auth.views.login', {'template_name': 'login.html'}),
	url(r'^logout$','django.contrib.auth.views.logout', {'next_page': '/login'}),
)

urlpatterns += patterns('intrepid_app.views',
	url(r'^$','index_view'),
	url(r'^index$','index_view'),
	url(r'^signup$','signup_view'),
	url(r'^profile/(?P<username>[0-9A-Za-z_@\+\-\.]+)$','profile_view'),
	url(r'^profile/(?P<username>[0-9A-Za-z_@\+\-\.]+)/edit$','edit_profile_view'),
	url(r'^trip/new$','new_trip_view'),
	url(r'^trip/(?P<trip_id>[0-9]+)$','trip_view'),
	url(r'^trip/(?P<trip_id>[0-9]+)/post$','new_post_view'),
	url(r'^trip/(?P<trip_id>[0-9]+)/finish$','finish_view'),
	url(r'^trip/(?P<trip_id>[0-9]+)/reactivate$','reactivate_view'),
	url(r'^trip/(?P<trip_id>[0-9]+)/delete$','delete_trip_view'),
	url(r'^file_upload$','file_upload_view'),
	url(r'^pin/(?P<pin_id>[0-9]+)/delete$','delete_pin_view'))

urlpatterns += patterns('',
	url(r'^api/(?P<username>[0-9A-Za-z_@\+\-\.]+)/trips/active',active_trip_resource))

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)