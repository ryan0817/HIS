from django.conf.urls import patterns, include, url

from django.contrib import admin

from HIS.views import new,parser, report, history, delete, edit, check, export

from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'HIS_PROJECT.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^new/',new),
    (r'^parser/',parser),
    (r'^report/',report),
    (r'^history/',history),
    (r'^delete/',delete),
    (r'^edit/',edit),
    (r'^check/',check),
    (r'^export/',export),
    url(r'^accounts/login/$',login),
    url(r'^accounts/logout/$','django.contrib.auth.views.logout_then_login'),
)
