from nio.block.base import Block
from nio.properties import VersionProperty, StringProperty, PropertyHolder, ObjectProperty, IntProperty
from nio.signal.base import Signal
import pyodbc
from nio.util.discovery import not_discoverable

class Credentials(PropertyHolder):

    userid = StringProperty(title='User ID', allow_none=True)
    password = StringProperty(title="Password", allow_none=True)

@not_discoverable
class MSSQLBase(Block):

    version = VersionProperty('0.1.0')
    server = StringProperty(title='Server')
    port = IntProperty(title='Port')
    database = StringProperty(title='Database')
    credentials = ObjectProperty(Credentials, title='Connection Credentials')

    def __init__(self):
        super().__init__()
        self.cnxn = None

    def configure(self, context):
        super().configure(context)
        cnxn_string = (
            'DRIVER={};'
            'PORT={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'PWD={}').format(
                '{ODBC Driver 13 for SQL Server}',
                self.port(),
                self.server(),
                self.database(),
                self.credentials().userid(),
                self.credentials().password())
        raw_cnxn_string = '%r'%cnxn_string  # cast to raw string literal
        self.cnxn = pyodbc.connect(raw_cnxn_string[1:-1]) # strip extra quotes apparently

    def stop(self):
        super().stop()
        self.cnxn.close()
