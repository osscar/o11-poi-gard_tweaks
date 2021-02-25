# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

import odoo.addons.decimal_precision as dp


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def write(self, vals):
        account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        cashier = self.env.user.has_group('gard_x_gard.group_cashier')
        deposit_id_val = 'deposit_id' in vals
        if any(state != 'draft' for state in set(self.mapped('state'))
            if not (account_edit or (cashier and deposit_id_val))):
            raise UserError(_("Edit allowed only in draft state."))
        else:
            return super().write(vals)
