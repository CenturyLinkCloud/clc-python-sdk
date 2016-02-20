#!/usr/bin/python

import json
import mock
from mock import patch, create_autospec
import unittest
import clc as clc_sdk
from clc.APIv2 import Servers, Server


# Python is not my primary language, so if this looks laughably simple,
# please correct it and make it better

class TestClcServer(unittest.TestCase):

    def setUp(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="base_test")
        self.test_obj = Server(id=12345, server_obj=True)

    def testDefaultConstructor(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="default")
        Server.Refresh = mock.MagicMock()
        svr = Server(id=42)
        self.assertEqual(1, clc_sdk.v2.Account.GetAlias.call_count)
        self.assertEqual(1, Server.Refresh.call_count)
        self.assertEqual(svr.id, 42)

    def testDefaultContructorFailedRefresh(self):
        clc_sdk.v2.Account.GetAlias = mock.MagicMock(return_value="default")
        Server.Refresh = mock.MagicMock(side_effect=self.get_mock_exception(error_code=404))
        with self.assertRaises(clc_sdk.CLCException):
            Server(id=42)

    # Lots of _Operation calls; might as well test them
    def testOperationErrorPath(self):
        clc_sdk.v2.API.Call = mock.MagicMock(side_effect=self.get_mock_exception(fail_json={'virus':'very yes'}))
        clc_sdk.v2.Requests = mock.MagicMock()
        self.test_obj._Operation(operation='whatever')
        clc_sdk.v2.Requests.assert_called_once_with({'virus':'very yes'},alias='base_test')

    def testOperationHappyPath(self):
        clc_sdk.v2.API.Call = mock.MagicMock()
        clc_sdk.v2.Requests = mock.MagicMock()
        self.test_obj._Operation(operation='whatever')
        clc_sdk.v2.API.Call.assert_called_once_with('POST','operations/base_test/servers/whatever','["12345"]')

    def testArchive(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.Archive()
        self.test_obj._Operation.assert_called_once_with('archive')

    def testPause(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.Pause()
        self.test_obj._Operation.assert_called_once_with('pause')

    def testShutDown(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.ShutDown()
        self.test_obj._Operation.assert_called_once_with('shutDown')

    def testReboot(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.Reboot()
        self.test_obj._Operation.assert_called_once_with('reboot')

    def testReset(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.Reset()
        self.test_obj._Operation.assert_called_once_with('reset')

    def testPowerOff(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.PowerOff()
        self.test_obj._Operation.assert_called_once_with('powerOff')

    def testPowerOn(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.PowerOn()
        self.test_obj._Operation.assert_called_once_with('powerOn')

    def testStartMaintenance(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.StartMaintenance()
        self.test_obj._Operation.assert_called_once_with('startMaintenance')

    def testStopMaintenance(self):
        self.test_obj._Operation = mock.MagicMock();
        self.test_obj.StopMaintenance()
        self.test_obj._Operation.assert_called_once_with('stopMaintenance')


    # Begin the endless stream of create tests...
    #
    # The ugly part of these is that we can't really test for the output, as we're
    # simply getting back a requests array without the raw submitted data.  Most
    # of these tests focus on validating input for exceptions/lack of exceptions
    def testCreateNoCpuException(self):
        with patch('clc.v2.Group') as mock_group:
            fake_group = mock.MagicMock()
            fake_group.Defaults.return_value = None
            mock_group.return_value = fake_group
            with self.assertRaises(clc_sdk.CLCException) as ex:
                Server.Create(name='x',template='x',group_id='x',network_id='x',alias='x')

        self.assertEqual(str(ex.exception), "No default CPU defined")


    def testCreateNoMemoryException(self):
        with patch('clc.v2.Group') as mock_group:
            fake_group = mock.MagicMock()
            fake_group.Defaults.return_value = None
            mock_group.return_value = fake_group
            with self.assertRaises(clc_sdk.CLCException) as ex:
                Server.Create(name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2)

        self.assertEqual(str(ex.exception), "No default Memory defined")

    def testCreateDefaultCpuAndMemory(self):
        with patch('clc.v2.Group') as mock_group:
            fake_group = mock.MagicMock()
            fake_group.Defaults.return_value = 42
            mock_group.return_value = fake_group
            clc_sdk.v2.API.Call = mock.MagicMock()
            clc_sdk.v2.Requests = mock.MagicMock()
            test = Server.Create(name='x',template='x',group_id='x',network_id='x',alias='x')
            # No assert -- if it doesn't blow up, it worked.  We hope.

    def testIllegalStorageType(self):
        with self.assertRaises(clc_sdk.CLCException) as ex:
            Server.Create(
                name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2,memory=2,storage_type="kaboom")
        self.assertEqual(str(ex.exception), "Invalid type/storage_type combo")

    def testHyperscaleWithStandard(self):
        with self.assertRaises(clc_sdk.CLCException) as ex:
            Server.Create(
                name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2,memory=2,
                type="hyperscale",storage_type="standard")
        self.assertEqual(str(ex.exception), "Invalid type/storage_type combo")

    def testHyperscaleWithPremium(self):
        with self.assertRaises(clc_sdk.CLCException) as ex:
            Server.Create(
                name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2,memory=2,
                type="hyperscale",storage_type="premium")
        self.assertEqual(str(ex.exception), "Invalid type/storage_type combo")

    def testStandardWithHyperscale(self):
        with self.assertRaises(clc_sdk.CLCException) as ex:
            Server.Create(
                name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2,memory=2,
                type="standard",storage_type="hyperscale")
        self.assertEqual(str(ex.exception), "Invalid type/storage_type combo")

    def testBadTTL(self):
        with self.assertRaises(clc_sdk.CLCException) as ex:
            Server.Create(
                name='x',template='x',group_id='x',network_id='x',alias='x',cpu=2,memory=2,ttl=10)
        self.assertEqual(str(ex.exception), "ttl must be greater than 3600 seconds")

    # End endless stream

    def testDelete(self):
        clc_sdk.v2.Requests = mock.MagicMock()
        clc_sdk.v2.API.Call = mock.MagicMock()
        self.test_obj.Delete()
        clc_sdk.v2.API.Call.assert_called_once_with('DELETE','servers/base_test/12345')

    # AddNIC tests

    def test_AddNIC_calls_api_when_no_ip_provided(self):
        clc_sdk.v2.Requests = mock.MagicMock()
        clc_sdk.v2.API.Call = mock.MagicMock()
        self.test_obj.AddNIC(network_id='test_network')
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            'servers/base_test/12345/networks',
            json.dumps({'networkId': 'test_network', 'ipAddress': ''})
            )

    def test_AddNIC_calls_api_with_provided_ip(self):
        clc_sdk.v2.Requests = mock.MagicMock()
        clc_sdk.v2.API.Call = mock.MagicMock()
        self.test_obj.AddNIC(network_id='test_network2', ip='1.2.3.4')
        clc_sdk.v2.API.Call.assert_called_once_with(
            'POST',
            'servers/base_test/12345/networks',
            json.dumps({'networkId': 'test_network2', 'ipAddress': '1.2.3.4'})
            )



    # Static helpers
    @staticmethod
    def get_mock_exception(error_code=None, fail_json=None):
        e = clc_sdk.APIFailedResponse("Fake message")
        if error_code:
            e.response_status_code = error_code
        if fail_json:
            e.response_json = fail_json
        return e

if __name__ == '__main__':
    unittest.main()
