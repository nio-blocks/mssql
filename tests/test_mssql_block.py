from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..mssql_block import MSSQL


class TestMSSQL(NIOBlockTestCase):

    _host = 'host'
    _db = 'db'
    _uid = 'user'
    _pw = 'pw'
    _driver = '{ODBC Driver 13 for SQL Server}'
    config = {
        'server': 'host',
        'database': 'db',
        'credentials': {'userid': _uid, 'password': _pw}}

    @patch(MSSQL.__module__ + '.pyodbc')
    def test_process_signals(self, mock_odbc):
        cnxn = mock_odbc.connect.return_value = MagicMock()
        """Signals pass through block unmodified."""
        blk = MSSQL()
        self.configure_block(blk, self.config)
        blk.start()
        blk.process_signals([Signal({"hello": "nio"})])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {"hello": "nio"})
        mock_odbc.connect.assert_called_once_with(
            'DRIVER={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'PWD={}'.format(
                self._driver,
                self._host,
                self._db,
                self._uid,
                self._pw))
        cnxn.close.assert_called_once()
