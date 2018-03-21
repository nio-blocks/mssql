from nio.properties import VersionProperty, StringProperty, Property
from nio.signal.base import Signal
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals


class MSSQLInsert(MSSQLBase):

    version = VersionProperty('0.1.0')
    row = Property(title='Row', default='{{ $.to_dict() }}')
    table = StringProperty(title='Target Table', default='')

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error(
                'Connection already in progress. Dropping signals.')
        else:
            output_signals = []
            try:
                cursor = self.cnxn.cursor()
            except e:
                if e.__class__ == pyodbc.ProgrammingError:
                    conn = self.connect()
                    cursor = self.cnxn.cursor()
            inserted = 0
            for signal in signals:
                row_dict = self.row(signal)
                cols = ''
                vals = ''
                for key in row_dict:
                    cols += key + ', '
                    val = row_dict[key]
                    if isinstance(val, str):
                        #double-up quote chars to escape without backslash
                        val = val.replace('\'', '\'\'').replace('\"', '\"\"')
                        val = '\'' + val + '\''
                    vals += str(val) + ', '
                query = 'INSERT INTO {} ({}) VALUES ({});'.format(
                    self.table(signal),
                    cols[:-2],
                    vals[:-2])
                self.logger.debug('Executing: {}'.format(query))
                result = cursor.execute(query)
                inserted += result.rowcount
            cursor.commit()
            cursor.close()
            self.logger.debug('Rows committed: {}'.format(inserted))
            self.notify_signals(Signal({'inserted': inserted}))
