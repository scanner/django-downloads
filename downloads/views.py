#!/usr/bin/env python
#
# File: $Id$
#
"""
The views for the download app.
"""

# system imports
#
import datetime
import mimetypes
import os.path
from urllib import quote, unquote

# Django imports
#
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _u
from django.db.models import Q
from django import forms

# 3rd party module imports
#
# http://trac.apricot.com/projects/django-asutils
from asutils.utils import asrender_to_response, msg_user
from asutils.sendfile import send_file
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign

# Form imports
#
from hackers.downloads.forms import DownloadableForm

# Model imports
#
from hackers.downloads.models import Downloadable, Download

####################################################################
#
def list(request, queryset, paginate_by, extra_context = None,
         template_name = 'downloads/list.html', **kwargs):
    """
    XXX Augment this with search capability like aswiki has

    A list of the downloads the user can see.

    Arguments:
    - `request`: django http request object
    - `queryset`: set of downloads to list
    - `paginate_by`: how many to display on a single page
    - `extra_context`: Dict to add to the request context
    - `template_name`: Template to use for rendering the result.
    """

    # XXX We need to filter out of the object list downloadables
    #     that the user does not have permission to see.
    return object_list(request, queryset, extra_context = extra_context,
                       template_name = template_name, **kwargs)

####################################################################
#
def create(request, extra_context = None, form_class = DownloadableForm,
           template_name = "downloads/create.html", **kwargs):
    """

    Arguments:
    - `request`:
    - `template_name`:
    """

    # Does this user have permission to create downloadloadable objects?
    #
    if not request.user.has_perm("downloads.add_downloadable"):
        return HttpResponseForbidden(_("You do not have permission to create a downloadable item."))

    # On POST we create the uploadable..
    #
    if request.method == 'POST' and 'content' in request.FILES:
        if 'content' in request.FILES:
            file_name = request.FILES['content'].name
            dnldbl = Downloadable(owner = request.user, content = file_name)
            form = form_class(request.POST, request.FILES, instance = dnldbl)
        else:
            dnldbl = Downloadable(owner = request.user, content = file_name)
            form = form_class(request.POST, instance = dnldbl)

        if form.is_valid():
            dnldbl = form.save(commit = False)
            dnldbl.owner = request.user
            dnldbl.save()

            # The owner gets permissions to his own objects.
            #
            assign('downloads.change_downloadable', request.user, dnldbl)
            assign('downloads.delete_downloadable', request.user, dnldbl)
            assign('downloads.view_downloadable', request.user, dnldbl)
            assign('downloads.download_downloadable', request.user, dnldbl)

            msg_user(request.user, _('File "%s" successfully uploaded') % \
                         os.path.basename(dnldbl.content.name))
            return HttpResponseRedirect(dnldbl.get_absolute_url())
    else:
        form = form_class()
    return asrender_to_response(request, template_name, { 'form' : form },
                                extra_context, **kwargs)


####################################################################
#
def details(request, downloadable_id, template_name = 'downloads/details.html',
            extra_context = None, **kwargs):
    """

    Arguments:
    - `request`:
    - `downloadable_id`:
    - `template_name`:
    - `extra_context`:
    - `**kwargs`:
    """
    dnldbl = get_object_or_404(Downloadable, pk = downloadable_id)
    if not request.user.has_perm('downloads.view_downloadable', dnldbl) and \
            request.user != dnldbl.owner:
        return HttpResponseForbidden(_("You do not have permission to view this downloadable item."))

    return asrender_to_response(request, template_name,
                                { 'downloadable' : dnldbl}, extra_context,
                                **kwargs)

####################################################################
#
def download(request, downloadable_id, extra_context = None, **kwargs):
    """

    Arguments:
    - `request`:
    - `downloadable_id`:
    - `extra_context`:
    - `**kwargs`:
    """

    dnldbl = get_object_or_404(Downloadable, pk = downloadable_id)
    if not request.user.has_perm('downloads.download_downloadable', dnldbl) and \
                        request.user != dnldbl.owner:
        return HttpResponseForbidden(_("You do not have permission to "
                                       "download this."))

    # Track that this download was request.
    #
    kwargs = { 'who' : request.user, 'what' : dnldbl }
    if 'REMOTE_ADDR' in request.META:
        kwargs['ip_address'] = request.META['REMOTE_ADDR']
    if 'REMOTE_HOST' in request.META:
        kwargs['dns_name'] = request.META['REMOTE_HOST']

    download = Download(**kwargs)
    download.save()

    # And then send the content to the requester.
    #
    # return send_file(request, dnldbl.content.path,
    #                  content_type = dnldbl.mimetype, blksize = 65536)
    return send_file(request, dnldbl.content.path,
                     content_type = "application/octet-stream", blksize = 65536)

####################################################################
#
def edit(request, downloadable_id, template_name = "downloads/edit.html",
         extra_context = None, form_class = DownloadableForm, **kwargs):
    """

    Arguments:
    - `request`:
    - `downloadable_id`:
    - `template_name`:
    - `extra_context`:
    - `**kwargs`:
    """

    dnldbl = get_object_or_404(Downloadable, pk = downloadable_id)
    if not request.user.has_perm('downloads.change_downloadable', dnldbl) and \
            request.user != dnldbl.owner:
        return HttpResponseForbidden(_("You do not have permission to change this downloadable item."))

    if request.method == "POST":
        # are we also uploading a new file with this edit?
        #
        if 'content' in request.FILES:
            file_name = request.FILES['content'].name
            dnldbl.content = file_name
            form = form_class(request.POST, request.FILES, instance = dnldbl)
        else:
            form = form_class(request.POST, instance = dnldbl)

        if form.is_valid():
            dnldbl = form.save()
            msg_user(request.user, "Downloadable updated.")
            return HttpResponseRedirect(dnldbl.get_absolute_url())
    else:
        form = form_class(instance = dnldbl)

    return asrender_to_response(request, template_name,
                                { 'downloadable' :dnldbl,
                                  'form'    : form },
                                extra_context, **kwargs)

####################################################################
#
def delete(request, downloadable_id, template_name = "downloads/delete.html",
           extra_context = None, **kwargs):
    """

    Arguments:
    - `request`:
    - `downloadable_id`:
    - `template_name`:
    - `extra_context`:
    - `**kwargs`:
    """

    dnldbl = get_object_or_404(Downloadable, pk = downloadable_id)
    if not request.user.has_perm('downloads.delete_downloadable', dnldbl) and \
            request.user != dnldbl.owner:
        return HttpResponseForbidden(_("You do not have permission to delete this downloadable item."))

    if request.method == "POST":
        # Delete the underlying file, and then delete the downloadable.
        #
        name = dnldbl.blurb
        dnldbl.content.delete()
        dnldbl.delete()
        msg_user(request.user, _("Downloadable %s deleted.") % name)
        return HttpResponseRedirect(reverse('downloads_list'))

    return asrender_to_response(request, template_name,
                                { 'downloadable' : dnldbl },
                                extra_context, **kwargs)



