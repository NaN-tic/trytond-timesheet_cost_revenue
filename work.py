# This file is part timesheet_cost_revenue module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
import datetime

from trytond.model import fields
from trytond.pyson import Eval, Id
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.tools import reduce_ids

__all__ = ['Work']


class Work:
    __metaclass__ = PoolMeta
    __name__ = 'timesheet.work'
    product = fields.Many2One('product.product', 'Product',
        domain=[
            ('type', '=', 'service'),
            ('default_uom_category', '=', Id('product', 'uom_cat_time')),
            ],
        states={
            'invisible': ~Eval('timesheet_available'),
            },
        depends=['timesheet_available'])
    list_price = fields.Numeric('List Price',
        digits=(16, Eval('currency_digits', 2)), depends=['currency_digits'])
    cost = fields.Function(fields.Numeric('Cost',
            states={
                'invisible': ~Eval('timesheet_available'),
                },
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits', 'timesheet_available']), 'get_cost')
    revenue = fields.Function(fields.Numeric('Revenue',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']), 'on_change_with_revenue')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')

    @classmethod
    def get_cost(cls, works, name):
        pool = Pool()
        Employee = pool.get('company.employee')
        Line = pool.get('timesheet.line')
        transaction = Transaction()
        cursor = transaction.connection.cursor()
        in_max = cursor.IN_MAX

        works = cls.search([
                ('parent', 'child_of', [w.id for w in works]),
                ('active', '=', True)])
        work_ids = [w.id for w in works]
        costs = dict.fromkeys(work_ids, 0)

        table_w = cls.__table__()
        table_c = cls.__table__()
        line = Line.__table__()

        employee_ids = set()
        for i in range(0, len(work_ids), in_max):
            sub_ids = work_ids[i:i + in_max]
            red_sql = reduce_ids(table_w.id, sub_ids)
            cursor.execute(*table_w.join(table_c,
                    condition=(table_c.left >= table_w.left)
                    & (table_c.right <= table_w.right)
                    ).join(line, condition=line.work == table_c.id
                    ).select(line.employee,
                    where=red_sql,
                    group_by=line.employee))
            employee_ids |= set(r[0] for r in cursor.fetchall())
        for employee in Employee.browse(list(employee_ids)):
            employee_costs = employee.get_employee_costs()
            to_date = None
            for from_date, cost in reversed(employee_costs):
                with transaction.set_context(
                        from_date=from_date,
                        to_date=to_date,
                        employees=[employee.id]):
                    for work in cls.browse(work_ids):
                        costs[work.id] += (
                            Decimal(str(work.hours)) * cost)
                to_date = from_date - datetime.timedelta(1)
        return costs

    @fields.depends('product', 'company')
    def on_change_with_list_price(self):
        pool = Pool()
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')
        Uom = pool.get('product.uom')
        Currency = pool.get('currency.currency')

        if not self.product:
            return self.list_price

        hour_uom = Uom(ModelData.get_id('product', 'uom_hour'))
        list_price = Uom.compute_price(self.product.default_uom,
            self.product.list_price, hour_uom)

        if self.company:
            user = User(Transaction().user)
            if user.company != self.company:
                if user.company.currency != self.company.currency:
                    list_price = Currency.compute(user.company.currency,
                        list_price, self.company.currency)

        return list_price

    @fields.depends('product', 'list_price', 'hours')
    def on_change_with_revenue(self, name=None):
        if self.list_price:
            return self.list_price * Decimal(str(self.hours))
        else:
            return Decimal(0)

    @fields.depends('company')
    def on_change_with_currency_digits(self, name=None):
        if self.company:
            return self.company.currency.digits
        return 2
