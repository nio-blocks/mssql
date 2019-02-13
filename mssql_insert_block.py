from nio.properties import VersionProperty, Property, StringProperty
from .mssql_base import MSSQLBase
from nio.block.mixins.enrich.enrich_signals import EnrichSignals


class MSSQLInsert(EnrichSignals, MSSQLBase):

    version = VersionProperty("1.0.0")
    table = StringProperty(title='Table', default='{{ $table }}', order=5)
    row = Property(title='Row', default='{{ $.to_dict() }}', order=6)

    def process_signals(self, signals):
        if self.isConnecting:
            self.logger.error(
                'Connection already in progress. Dropping signals.')
        else:
            output_signals = []
            try:
                cursor = self.cnxn.cursor()
            except Exception as e:
                self.disconnect()
                self.connect()
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
                        # double-up quote chars to escape without backslash hell
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
                output_signals.append(self.get_output_signal(
                    {'inserted': inserted}, signal))
            cursor.commit()
            cursor.close()
            self.logger.debug('Rows committed: {}'.format(inserted))
            self.notify_signals(output_signals)
