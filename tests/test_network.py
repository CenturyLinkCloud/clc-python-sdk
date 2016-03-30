#!/usr/bin/python

import mock
from mock import patch, create_autospec
import unittest
import clc as clc_sdk
from clc.APIv2 import Networks, Network


# Written by a non-Python developer
# Please make me better

class TestClcNetwork(unittest.TestCase):

    def setUp(self):
        data = {"name":"Name", "field1": "value1", "changeInfo": {"change1": "changeVal1"}}
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="base_test")
        self.test_obj = Network(id=12345, alias="007", network_obj=data)

    def testDefaultConstructor(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="default")
        clc_sdk.v2.API.Call = mock.MagicMock(return_value=None)
        obj = Network(id=42)
        assert clc_sdk.v2.Account.GetAlias.call_count == 1
        self.assertEqual(obj.id, 42)
        self.assertEqual(obj.alias, "default")

    def testConstructorAllArgs(self):
        net_obj = {"name": "testme", "other": "more_data"}
        obj = Network(id=43, alias="XYZ", network_obj=net_obj)
        self.assertEqual(obj.id, 43)
        self.assertEqual(obj.alias, "XYZ")
        self.assertEqual(obj.name, "testme")
        self.assertEqual(obj.data, net_obj)

    def testConstructorCallsRefreshWhenNetworkObjectNotProvided(self):
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="yup")
        data = {
            "id": "43",
            "cidr": "192.168.10.0/24",
            "description": "NiftyDescription",
            "gateway": "192.168.109.1",
            "name": "SparklyNewName",
            "netmask": "255.255.255.0",
            "type": "private",
            "vlan": 555,
            "links": []
        }
        clc_sdk.v2.API.Call = mock.MagicMock(return_value=data)

        obj = Network(id=43, alias="XYZ")

        self.assertEqual(obj.id, 43)
        self.assertEqual(obj.alias, "XYZ")
        self.assertEqual(obj.name, "SparklyNewName")
        self.assertEqual(obj.data, data)

    def testStringify(self):
        self.assertEqual(str(self.test_obj), "12345")

    def testGetAttrInData(self):
        self.assertEqual(self.test_obj.field1, "value1")
        self.assertEqual(self.test_obj.changeInfo['change1'], 'changeVal1')
        with self.assertRaises(AttributeError) as ex:
            self.test_obj.does_not_exist

    def testCreateNetworkGetsAbsentMembers(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="alias1")
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="location1")
        clc_sdk.v2.API.Call = mock.MagicMock(return_value="testing")
        clc_sdk.v2.Requests = mock.MagicMock()

        network = Network.Create()
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            '/v2-experimental/networks/alias1/location1/claim')
        clc_sdk.v2.Requests.assert_called_once_with("testing", alias="alias1")

    def testCreateNetworkWithAllArgs(self):
        clc_sdk.v2.API.Call = mock.MagicMock(return_value="testing")
        clc_sdk.v2.Requests = mock.MagicMock()

        network = Network.Create(alias='mock_alias', location='mock_dc')
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            '/v2-experimental/networks/mock_alias/mock_dc/claim')
        clc_sdk.v2.Requests.assert_called_once_with("testing", alias="mock_alias")

    def testDeleteNetworkGetsAbsentLocation(self):
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="location1")
        clc_sdk.v2.API.Call = mock.MagicMock()

        self.test_obj.Delete()
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            '/v2-experimental/networks/007/location1/12345/release')

    def testDeleteNetworkWithAllArgs(self):
        clc_sdk.v2.API.Call = mock.MagicMock()

        self.test_obj.Delete(location='location123')
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            '/v2-experimental/networks/007/location123/12345/release')

    def testUpdateNetworkGetsAbsentLocation(self):
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="location2")
        clc_sdk.v2.API.Call = mock.MagicMock()

        name = "Test Chickens Say 'Mock'"

        self.test_obj.Update(name)
        clc_sdk.v2.API.Call.assert_called_once_with(
            'PUT',
            '/v2-experimental/networks/007/location2/12345',
            {'name': name})

    def testUpdateNetworkWithAllArgs(self):
        clc_sdk.v2.API.Call = mock.MagicMock()

        name = "AwesomeMockNet"
        desc = "TestDesc"

        self.test_obj.Update(name, description=desc, location='location456')
        clc_sdk.v2.API.Call.assert_called_once_with(
            'PUT',
            '/v2-experimental/networks/007/location456/12345',
            {'name': name, 'description': desc})

    def testRefreshCallsGetLocationWhenLocationAbsent(self):
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="location222")
        clc_sdk.v2.API.Call = mock.MagicMock()

        self.test_obj.Refresh()
        clc_sdk.v2.Account.GetLocation.assert_called_once_with()

    def testRefreshCallsGetNetworkWithExpectedArgs(self):
        clc_sdk.v2.Account.GetLocation = mock.MagicMock(return_value="locationlocationlocation")
        clc_sdk.v2.API.Call = mock.MagicMock()

        self.test_obj.Refresh()
        clc_sdk.v2.API.Call.assert_called_once_with(
            'GET',
            '/v2-experimental/networks/007/locationlocationlocation/12345')

    def testRefreshUpdatesObjectData(self):
        new_name = "UpdatedNetworkName"
        new_desc = "UpdatedNetworkDesc"
        data = {
            "id": "12345",
            "cidr": "192.168.10.0/24",
            "description": new_desc,
            "gateway": "192.168.109.1",
            "name": new_name,
            "netmask": "255.255.255.0",
            "type": "private",
            "vlan": 555,
            "links": []
        }
        clc_sdk.v2.API.Call = mock.MagicMock(return_value=data)

        self.test_obj.Refresh()

        self.assertEqual(new_name, self.test_obj.name)
        self.assertEqual(new_desc, self.test_obj.description)

class TestClcNetworks(unittest.TestCase):

    def setUp(self):
        mock_output = [
            {
                "id": 12345,
                "cidr": "192.168.10.0/24",
                "name": "fake_network_one",
            },
            {
                "id": 54321,
                "cidr": "172.22.10.0/24",
                "name": "fake_network_two",
            },
            {
                "id": 90210,
                "cidr": "192.42.10.0/24",
                "name": "fake_network_three",
            }
        ]
        clc_sdk.v2.API.Call = mock.MagicMock(return_value=mock_output)
        self.test_obj = Networks(alias="007", location="TST")

    def testNoArgsConstructorThrowsException(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="default")
        with self.assertRaises(clc_sdk.CLCException) as ex:
            nets = Networks()
        assert clc_sdk.v2.Account.GetAlias.call_count == 1

    def testConstructorWithLocation(self):
        clc_sdk.v2.API.Call.assert_called_once_with('GET','/v2-experimental/networks/007/TST',{})

    def testConstructorWithNetworkList(self):
        data = [{"networkId": 24601, "accountID": "XYZ", "name": "NAME"}]
        test_obj = Networks(alias="007", networks_lst=data)
        self.assertEquals(len(test_obj.networks), 1)

    def testGetNetworkById(self):
        self.assertEqual(self.test_obj.Get(90210), self.test_obj.networks[2])

    def testGetNetworkByName(self):
        self.assertEqual(self.test_obj.Get("fake_network_one"), self.test_obj.networks[0])

    def testGetNetworkNoResult(self):
        self.assertEqual(self.test_obj.Get("nothing_here"), None)

    def testGetNetworkByCidr(self):
        self.assertEqual(self.test_obj.Get("172.22.10.0/24"), self.test_obj.networks[1])

if __name__ == '__main__':
    unittest.main()
