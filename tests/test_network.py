#!/usr/bin/python

import mock
from mock import patch, create_autospec
import unittest
from library.network import Networks, Network
import clc as clc_sdk


# Written by a non-Python developer
# Please make me better

class TestClcNetwork(unittest.TestCase):

    def setUp(self):
        data = {"name":"Name", "field1": "value1", "changeInfo": {"change1": "changeVal1"}}
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="base_test")
        self.test_obj = Network(id=12345, alias="007", network_obj=data)

    def testDefaultConstructor(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="default")
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

    def testStringify(self):
        self.assertEqual(str(self.test_obj), "12345")

    def testGetAttrInData(self):
        self.assertEqual(self.test_obj.field1, "value1")
        self.assertEqual(self.test_obj.change1, 'changeVal1')
        with self.assertRaises(AttributeError) as ex:
            self.test_obj.does_not_exist

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

if __name__ == '__main__':
    unittest.main()