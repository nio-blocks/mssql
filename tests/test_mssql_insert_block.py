from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_base import MSSQLBase
from ..mssql_insert_block import MSSQLInsert


class TestMSSQLInsert(NIOBlockTestCase):

    _host = 'host'
    _port = 314
    _db = 'db'
    _uid = 'user'
    _pw = 'pw'
    _driver = '{ODBC Driver 17 for SQL Server}'
    _mars = False
    config = {
        'connection': {
          'server': _host,
          'port': _port,
          'database': _db,
          'userid': _uid,
          'password': _pw,
          'mars': _mars,
        },
        'enrich': {
          'exclude_existing': False
        },
        'table': 'the_table'
    }

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.return_value = MagicMock()
        mock_cursor.execute.return_value = MagicMock(rowcount=1)
        blk = MSSQLInsert()
        self.configure_block(blk, self.config)

        signal_0 = {'a': 'a\"1', 'b': 2, 'c': 3}
        signal_1 = {'a': 'a\'2', 'c': 3}

        blk.start()
        blk.process_signals([
            Signal(signal_0),  # a contains double quote
            Signal(signal_1)])  # contains single quote
        blk.stop()
        self.assert_num_signals_notified(2)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'a': 'a\"1', 'b': 2, 'c': 3, 'inserted': 1})
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][1].to_dict(),
            {'a': "a'2", 'c': 3, 'inserted': 2})
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
                'no',
                self._pw))
        self.assertEqual(mock_cnxn.cursor.call_count, 1)
        self.assertEqual(mock_cursor.execute.call_count, 2)

        keys_0 = list(signal_0.keys())

        temp = {}
        for key in signal_0:
            try:
                temp[key] = signal_0[key].replace('a', '\'a').replace('1', '1\'').replace('\"', '\"\"')
            except:
                temp[key] = signal_0[key]
        self.assertEqual(
            mock_cursor.execute.call_args_list[0][0][0],
            'INSERT INTO the_table ({}, {}, {}) VALUES ({}, {}, {});'.format(
                    keys_0[0],
                    keys_0[1],
                    keys_0[2],
                    temp.get(keys_0[0]),
                    temp.get(keys_0[1]),
                    temp.get(keys_0[2])
            )
        )

        keys_1 = list(signal_1.keys())

        temp_1 = {}
        for key in signal_1:
            try:
                temp[key] = signal_1[key].replace('a', '\'a').replace('2', '\'2\'').replace('\"', '\"\"')
            except:
                temp[key] = signal_1[key]
        self.assertEqual(
            mock_cursor.execute.call_args_list[1][0][0],
            'INSERT INTO the_table ({}, {}) VALUES ({}, {});'.format(
                    keys_1[0],
                    keys_1[1],
                    temp.get(keys_1[0]),
                    temp.get(keys_1[1]),
            )
        )
        self.assertEqual(mock_cursor.commit.call_count, 1)
        self.assertEqual(mock_cursor.close.call_count, 1)
        self.assertEqual(mock_cnxn.close.call_count, 1)

    @patch(MSSQLBase.__module__ + '.pyodbc')
    def test_exception_handling(self, mock_odbc):
        mock_cnxn = mock_odbc.connect.return_value = MagicMock()
        mock_cursor = mock_cnxn.cursor.side_effect = Exception()
        blk = MSSQLInsert()
        self.configure_block(blk, self.config)

        blk.start()
        self.assertEqual(mock_odbc.connect.call_count, 1)
        with self.assertRaises(Exception):
            blk.process_signals([Signal({'a': 1})])
        mock_cnxn.close.assert_called_once_with()
        self.assertEqual(mock_odbc.connect.call_count, 2)
        self.assertEqual(mock_cnxn.cursor.call_count, 2)
        blk.stop()
