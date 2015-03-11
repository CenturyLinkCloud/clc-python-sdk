# -*- coding: utf-8 -*-
"""
CenturyLink Cloud Python SDK and CLI tool.

The CenturyLink Cloud Python SDK provides close to a one-to-one mapping between
the v1/v2 API calls within the library.

The CLI portion and other console entry points enable interactive and batch execution
of commands against the CenturyLink Cloud API in a platform independent manner.

CenturyLink Cloud: http://www.CenturyLinkCloud.com
Package Github page: https://github.com/CenturyLinkCloud/clc-python-sdk

API Documentaton v1: https://t3n.zendesk.com/categories/20012068-API-v1-0
API Documentaton v2: https://t3n.zendesk.com/categories/20067994-API-v2-0-Beta-

"""

from clc.APIv2.account import Account
from clc.APIv2.group import Group
from clc.APIv2.server import Servers, Server
from clc.APIv2.public_ip import PublicIPs, PublicIP
from clc.APIv2.disk import Disks, Disk
from clc.APIv2.network import Networks, Network
from clc.APIv2.template import Templates, Template
from clc.APIv2.alert import Alerts, Alert
from clc.APIv2.queue import Queue, Request, Requests
from clc.APIv2.anti_affinity import AntiAffinity
from clc.APIv2.datacenter import Datacenter
from clc.APIv2.api import API
import clc.APIv2.time_utils

import os
import sys


####### module/object vars #######
V2_API_USERNAME = False
V2_API_PASSWD = False
SSL_VERIFY = True

_V2_ENABLED = False
_LOGINS = 0
_BLUEPRINT_FTP_URL = False

def SetCredentials(api_username,api_passwd):
	"""Establish API username and password associated with APIv2 commands."""
	global V2_API_USERNAME
	global V2_API_PASSWD
	global _V2_ENABLED
	_V2_ENABLED = True
	V2_API_USERNAME = api_username
	V2_API_PASSWD = api_passwd


def SetSSLVerify(verify):
        """"Enable disable SSL Certfificate verification.
        # requests module includes cacert.pem which is visible when run as installed module.
        # pyinstall single-file deployment needs cacert.pem packaged along and referenced.
        # This module proxies between the two based on whether the cacert.pem exists in
        # the expected runtime directory.
        #
        # https://github.com/kennethreitz/requests/issues/557
        # http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
        #
        """
        global SSL_VERIFY
        if isinstance(verify, basestring):
            if os.path.isfile(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")),verify)):
                SSL_VERIFY = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")),verify)
            else: SSL_VERIFY = True
        else: SSL_VERIFY = verify
