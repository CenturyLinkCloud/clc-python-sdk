# -*- coding: utf-8 -*-
"""Private class that executes API calls."""

import requests
import xml.etree.ElementTree
import clc
import os
import sys


class API():
	
	@staticmethod
	def _DebugRequest(request,response):
		print('{}\n{}\n{}\n\n{}\n'.format(
			'-----------REQUEST-----------',
			request.method + ' ' + request.url,
			'\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
			request.body,
		))

		print('{}\n{}\n\n{}'.format(
			'-----------RESPONSE-----------',
			'status: ' + str(response.status_code),
			response.text
		))


	@staticmethod
	def _Login():
		"""Login to retrieve bearer token and set default accoutn and location aliases."""
		if not clc.v2.V2_API_USERNAME or not clc.v2.V2_API_PASSWD:
			clc.v1.output.Status('ERROR',3,'V2 API username and password not provided')
			raise(clc.APIV2NotEnabled)
			
		r = requests.post("%s/v2/%s" % (clc.defaults.ENDPOINT_URL_V2,"authentication/login"), 
						  data={"username": clc.v2.V2_API_USERNAME, "password": clc.v2.V2_API_PASSWD},
						  verify=clc.v2.SSL_VERIFY)

		if r.status_code == 200:
			clc._LOGIN_TOKEN_V2 = r.json()['bearerToken']
			clc.ALIAS = r.json()['accountAlias']
			clc.LOCATION = r.json()['locationAlias']
		elif r.status_code == 400:
			raise(Exception("Invalid V2 API login.  %s" % (r.json()['message'])))
		else:
			raise(Exception("Error logging into V2 API.  Response code %s. message %s" % (r.status_code,r.json()['message'])))


	@staticmethod
	def Call(method,url,payload={},debug=False):
		"""Execute v2 API call.

		:param url: URL paths associated with the API call
		:param payload: dict containing all parameters to submit with POST call

		:returns: decoded API json result
		"""
		if not clc._LOGIN_TOKEN_V2:  API._Login()

		# If executing refs provided in API they are abs paths,
		# Else refs we build in the sdk are relative
		if url[0]=='/':  fq_url = "%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)
		else:  fq_url = "%s/v2/%s" % (clc.defaults.ENDPOINT_URL_V2,url)

		headers = {'Authorization': "Bearer %s" % clc._LOGIN_TOKEN_V2}
		if isinstance(payload, basestring):  headers['content-type'] = "Application/json" # added for server ops with str payload

		if method=="GET":
			r = requests.request(method,fq_url,
								 headers=headers,
			                     params=payload, 
								 verify=clc.v2.SSL_VERIFY)
		else:
			r = requests.request(method,fq_url,
								 headers=headers,
			                     data=payload, 
								 verify=clc.v2.SSL_VERIFY)

		if debug:  
			API._DebugRequest(request=requests.Request(method,fq_url,data=payload,headers=headers).prepare(),
			                  response=r)

		if r.status_code>=200 and r.status_code<300:
			try:
				return(r.json())
			except:
				return({})
		else:
			try:
				e = clc.APIFailedResponse("Response code %s.  %s. %s %s" % 
				                          (r.status_code,r.json()['message'],method,"%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)))
				e.response_status_code = r.status_code
				e.response_json = r.json()
				e.response_text = r.text
				raise(e)
			except clc.APIFailedResponse:
				pass
			except:
				e = clc.APIFailedResponse("Response code %s. %s. %s %s" % 
				                         (r.status_code,r.text,method,"%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)))
				e.response_status_code = r.status_code
				e.response_json = {}	# or should this be None?
				e.response_text = r.text
				raise(e)


