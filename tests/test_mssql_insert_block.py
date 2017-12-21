from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_base_block import MSSQLBase
from ..mssql_insert_block import MSSQLInsert


class TestMSSQLInsert(NIOBlockTestCase):

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
        'table': 'the_table'}

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cnxn.cursor.return_value.execute.return_value = mock_cursor
        mock_cursor.rowcount = 1
        blk = MSSQLInsert()
        self.configure_block(blk, self.config)
        blk.start()
        blk.process_signals([Signal({'a': 1, 'b': 2, 'c': 3})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'inserted': 1})
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
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO the_table (a, b, c) VALUES (1, 2, 3);')
        mock_cursor.commit.assert_called_once()
        mock_cnxn.close.assert_called_once()
