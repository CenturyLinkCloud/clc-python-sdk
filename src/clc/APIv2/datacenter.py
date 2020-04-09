"""
Datacenter related functions.

These datacenter related functions generally align one-for-one with published API calls categorized in the account category

API v2 - https://t3n.zendesk.com/forums/21613140-Datacenters

Datacenter object variables:

	datacenter.id (alias for location)
	datacenter.name
	datacenter.location
	datacenter.supports_premium_storage
	datacenter.supports_shared_load_balancer

"""
from __future__ import print_function, absolute_import, unicode_literals

# TODO - init link to billing, statistics, scheduled activities
# TODO - accounts link?

import re
import clc

class Datacenter(object):  # pylint: disable=too-many-instance-attributes

	@staticmethod
	def Datacenters(alias=None, session=None):
		"""Return all cloud locations available to the calling alias.

		>>> clc.v2.Datacenter.Datacenters(alias=None)
		[<clc.APIv2.datacenter.Datacenter instance at 0x101462fc8>, <clc.APIv2.datacenter.Datacenter instance at 0x101464320>]

		"""
		if not alias:  alias = clc.v2.Account.GetAlias(session=session)

		datacenters = []
		for r in clc.v2.API.Call('GET','datacenters/%s' % alias,{}, session=session):
			datacenters.append(Datacenter(location=r['id'],name=r['name'],alias=alias,session=session))

		return(datacenters)


	def __init__(self,location=None,name=None,alias=None,session=None):
		"""Create Datacenter object.

		If parameters are populated then create object location.
		Else if only id is supplied issue a Get Policy call

		https://t3n.zendesk.com/entries/31026420-Get-Data-Center-Group

		"""

		self.deployment_capabilities = None
		self.baremetal_capabilities = None
		self.session = session

		if alias:
			self.alias = alias
		else:
			self.alias = clc.v2.Account.GetAlias(session=self.session)

		if location:
			self.location = location
		else:
			self.location = clc.v2.Account.GetLocation(session=self.session)

		if False:  # pylint: disable=using-constant-test
			# prepopulated info
			self.name = name
			self.location = location
			#self.servers = servers
		else:
			r = clc.v2.API.Call('GET','datacenters/%s/%s' % (self.alias,self.location),{'GroupLinks': 'true'}, session=session)
			self.name = r['name']
			self.root_group_id = [obj['id'] for obj in r['links'] if obj['rel'] == "group"][0]
			self.root_group_name = [obj['name'] for obj in r['links'] if obj['rel'] == "group"][0]

		self.id = self.location


	def RootGroup(self):
		"""Returns group object for datacenter root group.

		>>> clc.v2.Datacenter().RootGroup()
		<clc.APIv2.group.Group object at 0x105feacd0>
		>>> print _
		WA1 Hardware

		"""

		return(clc.v2.Group(id=self.root_group_id,alias=self.alias,session=self.session))


	def Groups(self):
		"""Returns groups object rooted at this datacenter.

		>>> wa1 = clc.v2.Datacenter.Datacenters()[0]
		>>> wa1.Groups()
		<clc.APIv2.group.Groups object at 0x10144f290>

		"""

		return(self.RootGroup().Subgroups())


	def _DeploymentCapabilities(self,cached=True):
		if not self.deployment_capabilities or not cached:
			self.deployment_capabilities = clc.v2.API.Call(
				'GET',
				'datacenters/%s/%s/deploymentCapabilities' % (self.alias,self.location),
				session=self.session)

		return(self.deployment_capabilities)


	def BareMetalCapabilities(self,cached=True):
		if self._DeploymentCapabilities()['supportsBareMetalServers']:
			if not self.baremetal_capabilities or not cached:
				self.baremetal_capabilities = clc.v2.API.Call(
					'GET',
					'datacenters/%s/%s/bareMetalCapabilities' % (self.alias,self.location),
					session=self.session)

		return(self.baremetal_capabilities)


	def Networks(self, forced_load=False):
		if forced_load:
			return(clc.v2.Networks(alias=self.alias, location=self.location, session=self.session))
		else:
			return(clc.v2.Networks(networks_lst=self._DeploymentCapabilities()['deployableNetworks'], session=self.session))


	def Templates(self):
		return(clc.v2.Templates(templates_lst=self._DeploymentCapabilities()['templates']))


	def __getattr__(self,var):
		key = re.sub("_(.)",lambda pat: pat.group(1).upper(),var)

		if key in ("supportsPremiumStorage","supportsSharedLoadBalancer"):  return(self._DeploymentCapabilities()[key])
		else:  raise(AttributeError("'%s' instance has no attribute '%s'" % (self.__class__.__name__,var)))


	def __str__(self):
		return(self.location)
