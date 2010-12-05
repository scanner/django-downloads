#!/usr/bin/env python
#
# File: $Id$
#
"""
Forms for the downloads app.
"""

# system imports
#

# Django imports
#
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

# Model imports
#
from hackers.downloads.models import Downloadable

##################################################################
##################################################################
#
class DownloadableForm(ModelForm):
    class Meta:
        model = Downloadable
