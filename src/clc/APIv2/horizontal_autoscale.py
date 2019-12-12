"""
HorizontalAutoscale related functions.

"""
from __future__ import print_function, absolute_import, unicode_literals

import json
import clc


class HorizontalAutoscalePolicy(object):

    def __init__(self, id_, policy_obj=None, alias=None, session=None):
        self.id = id_
        self.dirty = False
        self.session = session

        if alias:
            self.alias = alias
        else:
            self.alias = clc.v2.Account.GetAlias(session=self.session)

        if policy_obj:
            self.data = policy_obj
        else:
            try:
                self.Refresh()
            except clc.APIFailedResponse as e:
                if e.response_status_code == 404:
                    raise(clc.CLCException("Horizontal Autoscale Policy does not exist"))

    @staticmethod
    def GetAll(alias=None, session=None):
        if not alias:
            alias = clc.v2.Account.GetAlias(session=session)

        policies = []
        policies_lst = clc.v2.API.Call('GET', 'horizontalAutoscalePolicies/%s' % alias, {}, session=session)
        for policy in policies_lst['items']:
            policies.append(HorizontalAutoscalePolicy(policy['id'], policy, alias=alias, session=session))

        return policies

    @staticmethod
    def Create(policy_obj, alias=None, session=None):
        if not alias:
            alias = clc.v2.Account.GetAlias(session=session)

        policy = clc.v2.API.Call(
            'POST',
            'horizontalAutoscalePolicies/%s' % alias,
            json.dumps(policy_obj),
            session=session
        )

        return HorizontalAutoscalePolicy(policy['id'], policy, alias=alias, session=session)

    def Refresh(self):
        self.dirty = False
        self.data = clc.v2.API.Call(
            'GET',
            'horizontalAutoscalePolicies/%s/%s' % (self.alias, self.id),
            {},
            session=self.session
        )

    def Update(self, policy_obj):
        self.data = clc.v2.API.Call(
            'PUT',
            'horizontalAutoscalePolicies/%s/%s' % (self.alias, self.id),
            json.dumps(policy_obj),
            session=self.session
        )

    def Delete(self):
        self.dirty = True
        return clc.v2.API.Call(
            'DELETE',
            'horizontalAutoscalePolicies/%s/%s' % (self.alias, self.id),
            {},
            session=self.session
        )

    def ApplyToGroup(self, group_id):
        return clc.v2.API.Call(
            'PUT',
            'groups/%s/%s/horizontalAutoscalePolicy' % (self.alias, group_id),
            {"policyId": self.id},
            session=self.session
        )

    @staticmethod
    def RemoveFromGroup(group_id, alias=None, session=None):
        if not alias:
            alias = clc.v2.Account.GetAlias(session=session)

        return clc.v2.API.Call(
            'DELETE',
            'groups/%s/%s/horizontalAutoscalePolicy' % (alias, group_id),
            {},
            session=session
        )
