"""
Network related functions.

These network related functions generally align one-for-one with published API calls categorized in the network category

Networks object variables:

	networks.networks - list of all networks

Network object variables:

	network.name
	network.id
	network.type
	network.alias
	network.vlan
	network.netmask
	network.cidr
	network.type
	network.gateway
	network.description

"""


# TODO - create, change, delete NW  - pending API spec
# TODO - get network details (IP range, vlan, etc) - pending API spec
# TODO - filter NW by alias?


import re
import clc

class Networks(object):

	def __init__(self,alias=None,location=None,networks_lst=None):
		if alias:  self.alias = alias
		else:  self.alias = clc.v2.Account.GetAlias()

		self.networks = []
		if networks_lst:
			for network in networks_lst:
				self.networks.append(Network(id=network['networkId'],alias=network['accountID'],network_obj=network))
		elif location:
			self._Load(location)
		else:
			raise(clc.CLCException("Networks object requires location or networks_lst"))


	def _Load(self,location):
		"""Load all networks associated with the given location.

		https://www.centurylinkcloud.com/api-docs/v2/#get-network-list#request
		"""

		# https://api.ctl.io/v2-experimental/networks/ALIAS/WA1
		for network in clc.v2.API.Call('GET','/v2-experimental/networks/%s/%s' % (self.alias,location),{}):
			self.networks.append(Network(id=network['id'],alias=self.alias,network_obj=network))


	def Get(self,key):
		"""Get network by providing name, ID, or other unique key.

		If key is not unique and finds multiple matches only the first
		will be returned
		"""

		for network in self.networks:
			if network.id == key:  return(network)
			if network.name == key:  return(network)
			if network.cidr == key:  return(network)


class Network(object):

	def __init__(self,id,alias=None,network_obj=None):
		"""Create Network object."""

		self.id = id
		self.type = type
		self.dirty = False
		self.data = network_obj

		if alias:  self.alias = alias
		else:  self.alias = clc.v2.Account.GetAlias()

		if network_obj:  self.name = network_obj['name']
		else:
			try:
				self.Refresh()
			except clc.APIFailedResponse as e:
				if e.response_status_code==404:  raise(clc.CLCException("Network does not exist"))
				else: raise(clc.CLCException("An error occurred while creating the Network object"))

	@staticmethod
	def Create(alias=None,location=None):
		"""Claims a new network within a given account.

		https://www.ctl.io/api-docs/v2/#networks-claim-network

		Returns operation id and link to check status
		"""

		if not alias:  alias = clc.v2.Account.GetAlias()
		if not location:  location = clc.v2.Account.GetLocation()

		return clc.v2.Requests(
			clc.v2.API.Call('POST','/v2-experimental/networks/%s/%s/claim' % (alias, location)),
			alias=alias)

	def Delete(self,location=None):
		"""Releases the calling network.

		https://www.ctl.io/api-docs/v2/#networks-release-network

		Returns a 204 and no content
		"""

		if not location:  location = clc.v2.Account.GetLocation()

		return clc.v2.API.Call('POST','/v2-experimental/networks/%s/%s/%s/release' % (self.alias, location, self.id))

	def Update(self,name,description=None,location=None):
		"""Updates the attributes of a given Network via PUT.

		https://www.ctl.io/api-docs/v2/#networks-update-network

		{
      "name": "VLAN for Development Servers",
      "description": "Development Servers on 11.22.33.0/24"
		}

		Returns a 204 and no content
		"""

		if not location:  location = clc.v2.Account.GetLocation()

		payload = {'name': name}
		payload['description'] = description if description else self.description

		r = clc.v2.API.Call('PUT','/v2-experimental/networks/%s/%s/%s' % (self.alias, location, self.id), payload)

		self.name = self.data['name'] = name
		if description: self.data['description'] = description

	def Refresh(self, location=None):
		"""Reloads the network object to synchronize with cloud representation.

		>>> clc.v2.Network("f58148729bd94b02ae8b652f5c5feba3").Refresh()

		GET https://api.ctl.io/v2-experimental/networks/{accountAlias}/{dataCenter}/{Network}?ipAddresses=none|claimed|free|all
		"""
		if not location:  location = clc.v2.Account.GetLocation()

		new_object = clc.v2.API.Call('GET','/v2-experimental/networks/%s/%s/%s' % (self.alias,location,self.id))

		if new_object:
			self.name = new_object['name']
			self.data = new_object


	def __getattr__(self,var):
		key = re.sub("_(.)",lambda pat: pat.group(1).upper(),var)

		if key in self.data:  return(self.data[key])
		else:  raise(AttributeError("'%s' instance has no attribute '%s'" % (self.__class__.__name__,key)))


	def __str__(self):
		return(str(self.id))
