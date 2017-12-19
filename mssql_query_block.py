from nio.properties import VersionProperty, Property
from nio.signal.base import Signal
import pyodbc
from .mssql_base_block import MSSQLBase

class MSSQLQuery(MSSQLBase):

    version = VersionProperty('0.1.0')
    query = Property(title='Query', default='SELECT * from {{ $table }}')

    def process_signals(self, signals):
        output_signals = []
        cursor = self.cnxn.cursor()
        for signal in signals:
            rows = cursor.execute(self.query(signal)).fetchall()
            for row in rows:
                hashed_row = zip([r[0] for r in cursor.description], row)
                signal_dict = {a:b for a, b in hashed_row}
                output_signals.append(Signal(signal_dict))
        self.notify_signals(output_signals)
