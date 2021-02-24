# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

import odoo.addons.decimal_precision as dp


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def write(self, vals):
        if any(state != 'draft' for state in set(self.mapped('state'))):
            raise UserError(_("Edit allowed only in draft state."))
        else:
            return super().write(vals)
