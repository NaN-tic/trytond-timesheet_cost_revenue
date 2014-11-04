# This file is part timesheet_cost_revenue module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['Line']
__metaclass__ = PoolMeta


class Line():
    __name__ = 'timesheet.line'
    cost = fields.Function(fields.Numeric('Cost',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'on_change_with_cost')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')

    @fields.depends('employee', 'date', 'hours', 'work')
    def on_change_with_cost(self, name=None):
        if self.employee and self.hours and self.work:
            return self.compute_cost()
        return Decimal(0)

    @fields.depends('work')
    def on_change_with_currency_digits(self, name=None):
        if self.work:
            return self.work.currency_digits
        return 2
