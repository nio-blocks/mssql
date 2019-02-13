from nio.properties import VersionProperty, StringProperty
from nio.signal.base import Signal
from .mssql_base import MSSQLBase
from .mssql_conditions import MSSQLConditions


class MSSQLDelete(MSSQLBase, MSSQLConditions):

    version = VersionProperty("1.0.0")
    table = StringProperty(title='Table', default='{{ $table }}', order=5)

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error(
                'Connection already in progress. Dropping signals.')
        else:
            try:
                cursor = self.cnxn.cursor()
            except Exception as e:
                self.disconnect()
                self.connect()
                cursor = self.cnxn.cursor()

            total_rows = 0
            for signal in signals:
                # determine query to execute
                table = self.table(signal)
                conditions, params = \
                    self.get_where_conditions(signal, table, cursor)
                command = 'DELETE FROM {}'.format(table) + conditions
                self.logger.debug('Executing: {} with params {}'.format(
                    command, params))

                row_count = cursor.execute(command, params).rowcount
                self.logger.debug('{} rows returned for signal: {}'.
                                  format(row_count, signal.to_dict()))
                total_rows += row_count

            self.logger.debug('Rows deleted: {}'.format(total_rows))
            cursor.close()

            self.notify_signals([Signal({'Rows deleted': total_rows})])
