from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
import django.contrib.auth
from django.conf import settings
from django.conf.urls.static import static

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
	url(r'^post/new$','new_post_view'))

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)