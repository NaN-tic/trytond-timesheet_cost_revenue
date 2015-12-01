# This file is part of the timesheet_cost_revenue module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class TimesheetCostRevenueTestCase(ModuleTestCase):
    'Test Timesheet Cost Revenue module'
    module = 'timesheet_cost_revenue'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        TimesheetCostRevenueTestCase))
    return suite
