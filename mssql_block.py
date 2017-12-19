from nio.block.base import Block
from nio.properties import VersionProperty, StringProperty, PropertyHolder, ObjectProperty
import pyodbc

class Credentials(PropertyHolder):

    userid = StringProperty(title='User ID', allow_none=True)
    password = StringProperty(title="Password", allow_none=True)

class MSSQL(Block):

    version = VersionProperty('0.1.0')
    server = StringProperty(title='Server')
    database = StringProperty(title='Database')
    credentials = ObjectProperty(Credentials, title='Connection Credentials')

    def __init__(self):
        super().__init__()
        self.cnxn = None

    def configure(self, context):
        super().configure(context)
        cnxn_string = (
            'DRIVER={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'PWD={}')
        cnxn_string = cnxn_string.format(
            '{ODBC Driver 13 for SQL Server}',
            self.server(),
            self.database(),
            self.credentials().userid(),
            self.credentials().password())
        raw_cnxn_string = '%r'%cnxn_string  # cast to raw string literal
        self.cnxn = pyodbc.connect(raw_cnxn_string[1:-1])

    def process_signals(self, signals):
        for signal in signals:
            pass
        self.notify_signals(signals)

    def stop(self):
        super().stop()
        self.cnxn.close()
