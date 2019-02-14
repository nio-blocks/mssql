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
    _driver = '{ODBC Driver 17 for SQL Server}'
    _mars=True
    config = {
        'connection': {
          'server': _host,
          'port': _port,
          'database': _db,
          'user_id': _uid,
          'password': _pw,
          'mars': _mars,
        },
        'enrich': {
          'exclude_existing': False
        },
        'column_values': [],
        'conditions': []
    }

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cursor.execute.return_value = MagicMock(rowcount=1)
        blk = MSSQLUpdate()
        self.configure_block(blk, self.config)

        blk.start()
        blk.process_signals([Signal({'table': 'a_table'})])
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
            'MARS_Connection={};'
            'PWD={}'.format(
                self._driver,
                self._port,
                self._host,
                self._db,
                self._uid,
                'yes',
                self._pw))
        self.assertEqual(mock_cnxn.cursor.call_count, 1)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        self.assertEqual(mock_cursor.close.call_count, 1)
        self.assertEqual(mock_cnxn.close.call_count, 1)

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_exception_handling(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.side_effect = Exception()
        blk = MSSQLUpdate()
        self.configure_block(blk, self.config)

        blk.start()
        self.assertEqual(mock_odbc.connect.call_count, 1)
        with self.assertRaises(Exception):
            blk.process_signals([Signal({'a': 1})])
        mock_cnxn.close.assert_called_once_with()
        self.assertEqual(mock_odbc.connect.call_count, 2)
        self.assertEqual(mock_cnxn.cursor.call_count, 2)
        blk.stop()
