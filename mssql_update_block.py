from nio.properties import VersionProperty, Property
from nio.signal.base import Signal
from nio.block.terminals import output
from .mssql_base import MSSQLBase


class MSSQLUpdate(MSSQLBase):

    version = VersionProperty('0.1.0')
    update = Property(title='Update command', default='UPDATE SET {{ $data }}')

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error('Connection already in progress. Dropping signals.')
        else:
            try:
                cursor = self.cnxn.cursor()
            except e:
                if e.__class__ == pyodbc.OperationalError:
                    conn = self.connect()
                    cursor = self.cnxn.cursor()
            for signal in signals:
                update = self.update(signal)
                self.logger.debug('Executing: {}'.format(update))
                rows = cursor.execute(update).rowcount
                self.logger.debug('Rows updated: {}'.format(rows))
            cursor.close()

            self.notify_signals(Signal({'Rows updated': rows}))
