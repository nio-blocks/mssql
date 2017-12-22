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
    _driver = '{ODBC Driver 13 for SQL Server}'
    config = {
        'server': _host,
        'port': _port,
        'database': _db,
        'credentials': {'userid': _uid, 'password': _pw},
        'query': 'SELECT * from {{ $table }}'}

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
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'a': 1.0, 'b': 1.1, 'c': 1.2})
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][1].to_dict(),
            {'a': 2.0, 'b': 2.1, 'c': 2.2})
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][2].to_dict(),
            {'a': 3.0, 'b': 3.1, 'c': 3.2})
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
        mock_cnxn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with('SELECT * from foo')
        mock_cursor.close.assert_called_once()
        mock_cnxn.close.assert_called_once()
