from nio.properties import VersionProperty, StringProperty, Property
from nio.signal.base import Signal
from .mssql_base_block import MSSQLBase

class MSSQLInsert(MSSQLBase):

    version = VersionProperty('0.1.0')
    row = Property(title='Row', default='{{ $.to_dict() }}')
    table = StringProperty(title='Target Table', default='')

    def process_signals(self, signals):
        cursor = self.cnxn.cursor()
        output_signals = []
        for signal in signals:
            row_dict = self.row(signal)
            cols = ''
            vals = ''
            for key in row_dict:
                cols += key + ', '
                vals += str(row_dict[key]) + ', '
            query = 'INSERT INTO {} ({}) VALUES ({});'.format(
                self.table(signal),
                cols[:-2],
                vals[:-2])
            result = cursor.execute(query)
            output_signals.append(Signal({'inserted': result.rowcount}))
        cursor.commit()    
        self.notify_signals(output_signals)