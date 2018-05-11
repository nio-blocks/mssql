from nio.properties import VersionProperty, Property
from nio.signal.base import Signal
from nio.block.terminals import output
from .mssql_base import MSSQLBase


class MSSQLDelete(MSSQLBase):

    version = VersionProperty('0.1.0')
    command = Property(title='Command', default='DELETE * from {{ $table }}')

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error('Connection already in progress. Dropping signals.')
        else:
            output_signals = []
            try:
                cursor = self.cnxn.cursor()
            except e:
                self.disconnect()
                conn = self.connect()
                cursor = self.cnxn.cursor()
            for signal in signals:
                command = self.command(signal)
                self.logger.debug('Executing: {}'.format(command))
                rows = cursor.execute(command).rowcount
                self.logger.debug('Rows deleted: {}'.format(rows))
            cursor.close()

            self.notify_signals(Signal({'Rows deleted': rows }))
