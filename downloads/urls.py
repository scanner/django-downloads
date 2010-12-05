#!/usr/bin/env python
#
# File: $Id$
#
"""
URL's for the downloads app.
"""

# system imports
#

# Django imports
#
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse

# Models imports
#
from hackers.downloads.models import Downloadable

# If we have the 'asutils.middleware.RequireLogin' middleware then by
# default all of our views will require users to be logged in. This will
# fail for our rss feeds so, in that case we want to import the wrapper
# functions that we can use to require our rss feeds to use HTTP basic auth
# to authenticate a user. This is a bit backwards as we have to allow
# anonymous wrapped around the function that requires HTTP basic auth.
#
if 'asutils.middleware.RequireLogin' in settings.MIDDLEWARE_CLASSES:
    try:
        from asutils.decorators import view_or_basicauth
        from asutils.middleware import allow_anonymous

        @allow_anonymous
        def basic_auth_feed(request, url, feed_dict = None):
            args = (url,)
            kwargs = { 'feed_dict' : feed_dict }
            return view_or_basicauth(feed, request,
                                     lambda u: u.is_authenticated(),
                                     *args, **kwargs)
    except ImportError:
        def basic_auth_feed(request, url, feed_dict = None):
            return feed(request, url, feed_dict)

urlpatterns = patterns(
    '',

    # url('^$',
    #     redirect_to,
    #     { 'url' : reverse('downloads_list') },
    #     name = "downloads_index"),

    # View all available downloads.
    #
    url('^download/$',
        'hackers.downloads.views.list',
        { 'queryset'    : Downloadable.objects.all(),
          'paginate_by' : 20},
        name = "downloads_list"),

    # Create a new downloadable
    #
    url('^create/$',
        'hackers.downloads.views.create',
        name = 'downloads_create'),

    # View a specific downloadable
    #
    url('^download/(?P<downloadable_id>\d+)/$',
        'hackers.downloads.views.details',
        name = 'downloads_details'),

    # Download a specific downloadable
    #
    url('^download/(?P<downloadable_id>\d+)/download/$',
        'hackers.downloads.views.download',
        name = 'downloads_download'),

    # Edit a downloadable
    #
    url('^download/(?P<downloadable_id>\d+)/edit/$',
        'hackers.downloads.views.edit',
        name = 'downloads_edit'),

    # Delete a downloadable
    #
    url('^download/(?P<downloadable_id>\d+)/delete/$',
        'hackers.downloads.views.delete',
        name = 'downloads_delete'),

    )
