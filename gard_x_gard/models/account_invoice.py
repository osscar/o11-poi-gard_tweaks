# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        # if any((state == 'paid' for state in set(self.mapped('state')))):
        if any(state == 'paid' for state in set(self.mapped('state'))
            if not self.env.user.has_group('gard_x_gard.group_account_edit')):
            raise UserError(_("Edit allowed only in draft state."))
        else:
            return super().write(vals)
