from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import textinterface.views
import vcgen.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gettingstarted.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', textinterface.views.index, name='index'),
    url(r'^getconds/', vcgen.views.getconds, name='conditions'),
    url(r'^admin/', include(admin.site.urls)),

)
