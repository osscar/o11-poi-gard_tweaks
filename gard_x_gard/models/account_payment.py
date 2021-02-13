# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

import odoo.addons.decimal_precision as dp


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id')
    def _get_bank_info(self):
        if not self.journal_id:
            self.update({
                'bank': False,
                'bank_account_id': False,
                'card_bank_owner': False,
            })
            return
        if self.journal_id and self.journal_id.type == 'bank':
            values={
                'bank': self.journal_id.bank_id.id or False,
                'bank_account_id': self.journal_id.bank_account_id.id or False,
                'card_bank_owner': self.journal_id.card_bank_owner or False,
            }
            self.update(values)
        else:
            values={
                'bank': False,
                'bank_account_id': False,
                'card_bank_owner': False,
            }
            self.update(values)


