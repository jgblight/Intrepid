from django.conf.urls import patterns, include, url


from django.contrib import admin
admin.autodiscover()
import django.contrib.auth

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'intrepid.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^login$','django.contrib.auth.views.login', {'template_name': 'login.html'}),
	url(r'^logout$','django.contrib.auth.views.logout', {'next_page': '/login'}),
)

urlpatterns += patterns('intrepid_app.views',
	url(r'^$','index_view'),
	url(r'^signup$','signup_view'))