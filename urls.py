from django.conf.urls.defaults import *
from praetorian.auctions.feeds import MainFeed
from django.contrib import admin
admin.autodiscover()

feeds = dict(main=MainFeed)

urlpatterns = patterns('',
                       (r'^login/$', 'django.contrib.auth.views.login'),
                       (r'^accounts/login/$', 'django.contrib.auth.views.login'),                       
                       (r'^logout/$','django.contrib.auth.views.logout'),
                       (r'^accounts/password_change/$','django.contrib.auth.views.password_change'),
                       (r'^accounts/password_change/done/$','django.contrib.auth.views.password_change_done'),                                              
                       (r'^accounts/profile/$','praetorian.auctions.views.user_page'),
                       (r'^auction/(?P<auction_id>\d+)/$','praetorian.auctions.views.auction'),
                       (r'^auction/(?P<auction_id>\d+)/bid/$','praetorian.auctions.views.bid'),
                       (r'^check_for_winners/$','praetorian.auctions.views.check_for_winners'),
                       (r'^rules/$','praetorian.auctions.views.rules'),
                       (r'^welcome/$','praetorian.auctions.views.welcome'),                       
                       (r'^$','praetorian.auctions.views.index'),
                       (r'^admin/(.*)', admin.site.root),
                       (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/anders/code/python/praetorian/auctions/media/'}),
)
