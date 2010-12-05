#!/usr/bin/env python
#
# File: $Id$
#
"""
Declarations of our models so they appear in the django admin site.
"""

# system imports
#

# Django imports
#
from django.contrib import admin

# Model imports
#
from hackers.downloads.models import Downloadable, Download

##################################################################
##################################################################
#
class DownloadableAdmin(admin.ModelAdmin):
    list_display = ('id', 'blurb', 'content')
    list_filter = ('created', 'mimetype', 'owner')
    search_fields = ('blurb','description')

##################################################################
##################################################################
#
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'who', 'what', 'when')
    list_filter = ('when', 'who')
    search_fields = ('ip_address','dns_name')

admin.site.register(Downloadable, DownloadableAdmin)
admin.site.register(Download, DownloadAdmin)
