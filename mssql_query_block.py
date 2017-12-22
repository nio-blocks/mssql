from nio.properties import VersionProperty, Property
from nio.signal.base import Signal
from .mssql_base_block import MSSQLBase

class MSSQLQuery(MSSQLBase):

    version = VersionProperty('0.1.0')
    query = Property(title='Query', default='SELECT * from {{ $table }}')

    def process_signals(self, signals):
        output_signals = []
        cursor = self.cnxn.cursor()
        for signal in signals:
            query = self.query(signal)
            self.logger.debug('Executing: {}'.format(query))
            rows = cursor.execute(query).fetchall()
            self.logger.debug('Rows returned: {}'.format(len(rows)))
            for row in rows:
                hashed_row = zip([r[0] for r in cursor.description], row)
                signal_dict = {a:b for a, b in hashed_row}
                output_signals.append(Signal(signal_dict))
        self.notify_signals(output_signals)
