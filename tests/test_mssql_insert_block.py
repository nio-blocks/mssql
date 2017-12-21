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
        blk.process_signals([
            Signal({'a': 1, 'b': 2, 'c': 3}),
            Signal({'a': 2, 'b': 3, 'c': 4})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'inserted': 2})
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
        self.assertEqual(mock_cursor.execute.call_count, 2)
        self.assertEqual(
            mock_cursor.execute.call_args_list[0][0][0],
            'INSERT INTO the_table (a, b, c) VALUES (1, 2, 3);')
        self.assertEqual(
            mock_cursor.execute.call_args_list[1][0][0],
            'INSERT INTO the_table (a, b, c) VALUES (2, 3, 4);')
        mock_cursor.commit.assert_called_once()
        mock_cnxn.close.assert_called_once()
