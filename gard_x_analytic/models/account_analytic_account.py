# -*- coding: utf-8 -*-

from odoo import api, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    # _rec_name = "move_id"

    _sql_constraints = [
        ('unique_code', 'unique (code)', 'The analytic account code must be unique.')
    ]

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        parent_acc = self.parent_id

        # get department from parent
        if parent_acc and parent_acc.department_id:
            self.department_id = parent_acc.department_id
