#
# File: $Id: models.py 1922 2008-11-14 08:26:58Z scanner $
#

# Python standard lib imports
#
import os.path

# Django imports
#
from django.db import models
from django.conf import settings
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
import django.dispatch

# Model imports
#
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# 3rd party module imports
#
try:
    import tagging
except ImportError:
    tagging = None
try:
    import notification
except ImportError:
    notification = None

# Because downloads serves up downloadable file content and because these bits
# of content may be restricted by permissions we can not have these uploaded
# files sitting under MEDIA_ROOT. If they were someone could retrieve them if
# they knew the path name without going through our permission system at
# all. This is bad, even though serving them up ourselves is expensive I do
# not see where we have a choice as for some people the content may be
# sensitive. We create our own FileSystemStorage object that points at this
# location. Of course, if the setting for DOWNLOADS_UPLOAD_ROOT was not set,
# then we fall back to MEDIA_ROOT.
#
fs = FileSystemStorage(location = getattr(settings, "DOWNLOADS_UPLOAD_ROOT",
                                          os.path.join(settings.MEDIA_ROOT,
                                                       'downloads')))

# We define a signal that is invoked whenever an uploadable is created.
# Primarily used to generate notifications and generate the thumbnail/preview
# image.
#
uploadable_created = django.dispatch.Signal()

MIME_TYPES = (
    ('text/plain', 'plain text'),
    ('application/octet-stream', 'binary file'),
    ('application/zip', 'zip file'),
    ('application/x-gzip', 'gzip file'),
    ('application/x-tar', 'tar file'),
    )

##################################################################
##################################################################
#
class Downloadable(models.Model):
    """
    The core object of this app - a downloadable something or other.
    We treat all of these as simple file attachments.
    We may have a preview image of the attachment.
    """
    owner = models.ForeignKey(User, verbose_name = _('owner'),
                              editable = False, db_index = True,
                              help_text = _('The user that uploaded this '
                                            'file.'))
    blurb = models.CharField(_("blurb"), max_length = 256,
                             help_text = _('A short description of this file.'))
    description = models.TextField(_("description"), max_length = 2048,
                                   blank = True,
                                   help_text = _("A longer description of "
                                                 "this file"))
    content = models.FileField(_('content'), max_length = 1024,
                               null = True,
                               storage = fs, db_index = True,
                               upload_to = "files/%Y/%m/%d")
    created = models.DateTimeField(_('created'), auto_now_add = True,
                                   editable = False, db_index = True,
                                   help_text = _('The time at which '
                                                 'this file was '
                                                 'originally uploaded.'))
    mimetype = models.CharField(_("mime type"), max_length = 128,
                                choices = MIME_TYPES,
                                default = 'application/octet-stream',
                                help_text = _("The mime type of this "
                                              "downloadable file."))
    thumbnail = models.ImageField(_('thumbnail'), max_length = 1024,
                                  storage = fs, null = True, blank = True,
                                  editable = False,
                                  upload_to = "thumbnails/%Y/%m/%d",
                                  help_text = _('A thumbnail preview of '
                                                'the file, if we have a '
                                                'way of rendering it.'))

    class Meta:
        permissions = (
            ('view_downloadable', 'View downloadable'),
            ('download_downloadable', 'Download downloadable'),
            )

    ##################################################################
    #
    def __unicode__(self):
        if self.content:
            return u"<id: %d, File: '%s', mimetype: %s>" % (self.id,
                                                            self.content,
                                                            self.mimetype)
        else:
            return u"<id: %d, File: No file, mimetype: %s>" % (self.id,
                                                               self.mimetype)

    ##################################################################
    #
    @permalink
    def get_absolute_url(self):
        return ('downloads_details', (self.id,))

if tagging:
    # We register the Downloadable model with the tagging module - this gives
    # all of our Downloadables's the ability to have tags.
    #
    tagging.register(Downloadable)

##################################################################
##################################################################
#
class Download(models.Model):
    """
    This class is used to track downloads of a downloadable. Who
    downloaded what, when, how often, and from where.

    We store at least usre, date, ip address and what was downloaded.
    We may also resolve the ip address shortly after the download
    happens and store that separately in the 'hostname' attribute.

    The reason for the hostname as well as the IP address is that
    hostnames change over time and we may care what the host was when
    it happened, not when we need to resolve these names days, weeks
    or months later.
    """
    who = models.ForeignKey(User, verbose_name = _("who"), db_index = True,
                            help_text = _("Who downloaded the file."))
    what = models.ForeignKey(Downloadable, verbose_name = _("what"),
                             db_index = True,
                             help_text = _("What file was downloaded."))
    when = models.DateTimeField(_("when"), auto_now_add = True,
                                editable = False, db_index = True)
    ip_address = models.CharField(_("IP Address"), max_length = 256,
                                  help_text = _("The IP address a file was "
                                                "downloaded from."))
    dns_name = models.CharField(_("DNS Name"), max_length = 1024,
                                null = True,
                                help_text = _("The DNS name of the host "
                                              "a file was downloaded from "
                                              "at the time the download "
                                              "happend"))

    ##################################################################
    #
    def __unicode__(self):
        if self.dns_name and self.dns_name != "":
            return "<Download of '%s' by '%s' at %s from %s (%s)>" % \
                (self.what.download, self.who.username, self.when,
                 self.ip_address, self.dns_name)
        else:
            return "<Download of '%s' by '%s' at %s from %s>" % \
                (self.what.download, self.who.username, self.when,
                 self.ip_address)

