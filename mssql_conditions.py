from enum import Enum
from nio.properties import ListProperty, Property, SelectProperty, StringProperty, PropertyHolder


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
    operation = SelectProperty(Operator, title='Operator', default="EQ", order=21)
    value = Property(title='Value', order=22)


class MSSQLConditions(object):
    conditions = ListProperty(Conditions, title='Conditions', default=[], order=15)
    combine_condition = SelectProperty(AndOrOperator, title='Combine Condition', default="AND", order=14)

    def _get_where_conditions(self, signal, table, cursor):
        conditions = ""
        combine_condition = self.combine_condition().value
        params = []
        for i, condition in enumerate(self.conditions()):
            if i == 0:
                conditions += ' WHERE '
            else:
                conditions += ' {} '.format(combine_condition)

            column = self.validate_column(condition.column(signal), table, cursor)
            condition_string = '{} {} ?'.format(column, condition.operation(signal).value)

            conditions += condition_string
            params.append(condition.value(signal))
        return conditions, params
