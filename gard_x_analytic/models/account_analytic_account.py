# -*- coding: utf-8 -*-

from odoo import api, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    # _sql_constraints = [
    #     ('unique_code', 'UNIQUE (code)', _('The analytic account code must be unique.'))
    # ]

    @api.multi
    @api.constrains("firstname", "lastname")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if all((
                record.type == 'contact' or record.is_company,
                not (record.firstname or record.lastname)
            )):
                raise exceptions.EmptyNamesError(record)

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        parent_acc = self.parent_id

        # get department from parent
        if parent_acc and parent_acc.department_id:
            self.department_id = parent_acc.department_id
