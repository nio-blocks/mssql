from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_base import MSSQLBase
from ..mssql_query_block import MSSQLQuery


class TestMSSQL(NIOBlockTestCase):

    _host = 'host'
    _port = 314
    _db = 'db'
    _uid = 'user'
    _pw = 'pw'
    _driver = '{ODBC Driver 17 for SQL Server}'
    config = {
        'server': _host,
        'port': _port,
        'database': _db,
        'credentials': {'userid': _uid, 'password': _pw},
        'query': 'SELECT * from {{ $table }}',
        'enrich': {'exclude_existing': False}
    }

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1.0, 1.1, 1.2),
            (2.0, 2.1, 2.2),
            (3.0, 3.1, 3.2)]
        mock_cursor.description = (('a',), ('b',), ('c',))
        blk = MSSQLQuery()
        self.configure_block(blk, self.config)
        blk.start()
        blk.process_signals([Signal({'table': 'foo'})])
        blk.stop()
        self.assert_num_signals_notified(3)
        self.assertDictEqual(
            self.last_notified['results'][0].to_dict(),
            {'a': 1.0, 'b': 1.1, 'c': 1.2, 'table': 'foo'})
        self.assertDictEqual(
            self.last_notified['results'][1].to_dict(),
            {'a': 2.0, 'b': 2.1, 'c': 2.2, 'table': 'foo'})
        self.assertDictEqual(
            self.last_notified['results'][2].to_dict(),
            {'a': 3.0, 'b': 3.1, 'c': 3.2, 'table': 'foo'})
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
        mock_cursor.execute.assert_called_once_with('SELECT * from foo')
        self.assertEqual(mock_cursor.close.call_count, 1)
        self.assertEqual(mock_cnxn.close.call_count, 1)

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_null_results(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        blk = MSSQLQuery()
        self.configure_block(blk, self.config)
        blk.start()
        blk.process_signals([Signal({'table': 'foo'})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified['no_results'][0].to_dict(),
                    {'results': 'null', 'table': 'foo'})
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
        mock_cursor.execute.assert_called_once_with('SELECT * from foo')
        self.assertEqual(mock_cursor.close.call_count, 1)
        self.assertEqual(mock_cnxn.close.call_count, 1)

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.side_effect = Exception()
        blk = MSSQLQuery()
        self.configure_block(blk, self.config)

        blk.start()
        self.assertEqual(mock_odbc.connect.call_count, 1)
        with self.assertRaises(Exception):
            blk.process_signals([Signal({'a': 1})])
        mock_cnxn.close.assert_called_once_with()
        self.assertEqual(mock_odbc.connect.call_count, 2)
        self.assertEqual(mock_cnxn.cursor.call_count, 2)
        blk.stop()
