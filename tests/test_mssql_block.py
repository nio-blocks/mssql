from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_base_block import MSSQLBase
from ..mssql_query_block import MSSQLQuery


class RowObject(object):

    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

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
        self.maxDiff = None
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cnxn.cursor.return_value.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            RowObject(a=1.0, b=1.1, c=1.2),
            RowObject(a=2.0, b=2.1, c=2.2),
            RowObject(a=3.0, b=3.1, c=3.2)]
        """Signals pass through block unmodified."""
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
        mock_cnxn.cursor.return_value.execute.assert_called_once_with('SELECT * from foo')
        mock_cnxn.close.assert_called_once()
