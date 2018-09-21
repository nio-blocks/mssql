from enum import Enum

from .mssql_column import validate_column
from nio.properties import ListProperty, Property, SelectProperty, \
                           StringProperty, PropertyHolder


class Operator(Enum):

    EQ = '='
    GT = '>'
    GTE = '>='
    LT = '<'
    LTE = '<='
    NOT = '!='


class AndOrOperator(Enum):

    AND = 'AND'
    OR = 'OR'


class Conditions(PropertyHolder):

    column = StringProperty(title='Column', order=20)
    operation = SelectProperty(Operator, title='Operator',
                               default="EQ", order=21)
    value = Property(title='Value', order=22)
    combine_condition = SelectProperty(AndOrOperator, title='Combine Condition',
                                       default="AND", order=23)


class MSSQLConditions(object):

    conditions = ListProperty(Conditions,
                              title='Conditions',
                              deafult=[],
                              order=14)

    def get_where_conditions(self, signal, table, cursor):
        conditions = ""
        params = []
        for i, condition in enumerate(self.conditions()):
            if i == 0:
                conditions += ' WHERE '
            else:
                conditions += ' {} '.format(combine_condition)

            condition_string = '{} {} ?'.format(
                validate_column(condition.column(signal), table, cursor),
                condition.operation(signal).value)
            conditions += condition_string
            params.append(condition.value(signal))

            # grab combine condition to apply for next
            combine_condition = condition.combine_condition(signal).value
        return conditions, params
