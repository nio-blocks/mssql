from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_base import MSSQLBase
from ..mssql_update_block import MSSQLUpdate


class TestMSSQLUpdate(NIOBlockTestCase):

    _host = 'host'
    _port = 314
    _db = 'db'
    _uid = 'user'
    _pw = 'pw'
    _driver = '{ODBC Driver 13 for SQL Server}'
    config = {
        'server': _host,
        'port': _port,
        'database': _db,
        'credentials': {'userid': _uid, 'password': _pw},
        'command': 'UPDATE SET {{ $data }}'
    }

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cursor.execute.return_value = MagicMock(rowcount=1)
        blk = MSSQLUpdate()
        self.configure_block(blk, self.config)

        signal_0 = {'data': 'testData'}

        blk.start()
        blk.process_signals([Signal(signal_0)])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'Rows updated': 1})
        mock_odbc.connect.assert_called_once_with(
            'DRIVER={};'
            'PORT={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'PWD={}'.format(
                self._driver,
                self._port,
                self._host,
                self._db,
                self._uid,
                self._pw))
        self.assertEqual(mock_cnxn.cursor.call_count, 1)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        self.assertEqual(mock_cursor.close.call_count, 1)
        self.assertEqual(mock_cnxn.close.call_count, 1)
