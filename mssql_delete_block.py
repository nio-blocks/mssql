from nio.properties import VersionProperty, StringProperty
from nio.signal.base import Signal

from .mssql_tabled_base import MSSQLTabledBase
from .mssql_conditions import MSSQLConditions


class MSSQLDelete(MSSQLTabledBase, MSSQLConditions):
    version = VersionProperty("1.0.1")

    def process_signals(self, signals):
        if self.is_connecting:
            self.logger.error('Connection already in progress. Dropping signals.')
            return

        cursor = self._get_cursor()

        total_rows = 0
        for signal in signals:
            # determine query to execute
            table = self.table()
            conditions, params = \
                self._get_where_conditions(signal, table, cursor)
            command = 'DELETE FROM {}'.format(table) + conditions
            self.logger.debug('Executing: {} with params {}'.format(
                command, params))

            row_count = cursor.execute(command, params).rowcount
            self.logger.debug('{} rows returned for signal: {}'.
                              format(row_count, signal.to_dict()))
            total_rows += row_count

        self.logger.debug('Rows deleted: {}'.format(total_rows))
        cursor.commit()
        cursor.close()

        self.notify_signals([Signal({'Rows deleted': total_rows})])
