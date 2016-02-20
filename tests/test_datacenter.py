#!/usr/bin/python

import mock
from mock import patch, create_autospec
import unittest
import clc as clc_sdk
from clc.APIv2 import Datacenter


# Written by a non-Python developer
# Please make me better

class TestClcDatacenter(unittest.TestCase):

    def setUp(self):
        dcs = {
            "name": "test_dc_name",
            "links": [{"rel": "group", "id": "test_group_id", "name": "test_group_name"}]
        }
        clc_sdk.v2.API.Call = mock.MagicMock(return_value=dcs)
        self.test_obj = Datacenter(location="test123", alias="007", )

    def testDefaultConstructor(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="mock_alias")
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="mock_loc")
        obj = Datacenter()
        assert clc_sdk.v2.Account.GetAlias.call_count == 1
        assert clc_sdk.v2.Account.GetLocation.call_count == 1
        clc_sdk.v2.API.Call.assert_called_with('GET','datacenters/mock_alias/mock_loc',{'GroupLinks': 'true'})
        self.assertEqual(obj.id, "mock_loc")
        self.assertEqual(obj.name, "test_dc_name")
        self.assertEqual(obj.alias, "mock_alias")
        self.assertEqual(obj.location, "mock_loc")
        self.assertEqual(obj.root_group_id, "test_group_id")
        self.assertEqual(obj.root_group_name, "test_group_name")

    def testConstructorAllArgs(self):
        clc_sdk.v2.API.Call.assert_called_once_with('GET','datacenters/007/test123',{'GroupLinks': 'true'})
        self.assertEqual(self.test_obj.id, "test123")
        self.assertEqual(self.test_obj.name, "test_dc_name")
        self.assertEqual(self.test_obj.alias, "007")
        self.assertEqual(self.test_obj.location, "test123")
        self.assertEqual(self.test_obj.root_group_id, "test_group_id")
        self.assertEqual(self.test_obj.root_group_name, "test_group_name")

    def testStringify(self):
        self.assertEqual(str(self.test_obj), "test123")

    def testNetworks(self):
        clc_sdk.v2.Networks = mock.MagicMock(return_value="hello")
        clc_sdk.v2.API.Call = mock.MagicMock(return_value={"deployableNetworks": "network_list"})
        me = self.test_obj.Networks()
        clc_sdk.v2.Networks.assert_called_once_with(networks_lst="network_list")

    def testNetworksWithForcedLoad(self):
        clc_sdk.v2.Networks = mock.MagicMock(return_value="hello")
        me = self.test_obj.Networks(forced_load=True)
        clc_sdk.v2.Networks.assert_called_once_with(alias="007", location="test123")


if __name__ == '__main__':
    unittest.main()
