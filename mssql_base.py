import pyodbc
from nio.block.base import Block
from nio.properties import (StringProperty, IntProperty, BoolProperty, ObjectProperty, PropertyHolder)
from nio.util.discovery import not_discoverable


class Connection(PropertyHolder):
    server = StringProperty(title='Server', default='[[MSSQL_SERVER]]', order=1)
    port = IntProperty(title='Port', default='[[MSSQL_PORT]]', order=2)
    database = StringProperty(title='Database', default='[[MSSQL_DB]]', order=3)
    user_id = StringProperty(title='User ID', allow_none=True, default='[[MSSQL_USER]]', order=4)
    password = StringProperty(title='Password', allow_none=True, default='[[MSSQL_PWD]]', order=5)

class Mars(PropertyHolder):
    enabled = BoolProperty(title='Enable MARS?', default=True, order=1)

@not_discoverable
class MSSQLBase(Block):
    connection = ObjectProperty(Connection, title='Database Connection', order=50)
    mars = ObjectProperty(Mars, title='Multiple Active Result Sets (MARS)', order=60)

    def __init__(self):
        super().__init__()
        self.cnxn = None
        self.is_connecting = False

    def configure(self, context):
        super().configure(context)
        self.connect()

    def connect(self):
        self.is_connecting = True

        cnxn_props = self.connection()
        mars_enabled = self.mars().enabled()

        cnxn_string = (
            'DRIVER={};'
            'PORT={};'
            'SERVER={};'
            'DATABASE={};'
            'UID={};'
            'MARS_Connection={};'
            'PWD={}').format(
                '{ODBC Driver 17 for SQL Server}',
                cnxn_props.port(),
                cnxn_props.server(),
                cnxn_props.database(),
                cnxn_props.user_id(),
                'yes' if mars_enabled else 'no',
                cnxn_props.password())
        self.logger.debug('Connecting: {}'.format(cnxn_string))
        self.cnxn = pyodbc.connect(cnxn_string)
        self.is_connecting = False

    def disconnect(self):
        if self.cnxn:
            self.cnxn.close()
            self.cnxn = None

    def stop(self):
        super().stop()
        self.disconnect()

    def _get_cursor(self):
        try:
            return self.cnxn.cursor()
        except Exception as e:
            self.disconnect()
            self.connect()
            return self.cnxn.cursor()
