# This file is part timesheet_cost_revenue module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .work import *


def register():
    Pool.register(
        Work,
        module='timesheet_cost_revenue', type_='model')
