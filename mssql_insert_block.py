from nio.properties import VersionProperty, Property
from nio.block.mixins.enrich.enrich_signals import EnrichSignals

from .mssql_tabled_base import MSSQLTabledBase

class MSSQLInsert(EnrichSignals, MSSQLTabledBase):
    version = VersionProperty("1.0.1")
    row = Property(title='Row', default='{{ $.to_dict() }}', order=2)

    def process_signals(self, signals, **kwargs):
        if self.is_connecting:
            self.logger.error('Connection already in progress. Dropping signals.')
            return

        output_signals = []
        cursor = self._get_cursor()

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
                self.table(),
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
