# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends("state")
    def _get_warehouse(self):
        res = super(AccountInvoice, self)._get_warehouse()
        for invoice in self:
            if invoice.cc_dos and invoice.type == "out_invoice":
                if invoice.cc_dos and not invoice.cc_dos.warehouse_id.journal_id:
                    raise ValidationError(
                        _("A journal must be set for the dosification branch.")
                    )
                else:
                    # set appropriate sale journal based on cc_dos.warehouse_id.journal_id
                    invoice.journal_id = invoice.cc_dos.journal_id
        return res

    @api.onchange("cc_dos")
    def _onchange_cc_dos(self):
        # find the right journal when changing dosification on invoice
        if self.cc_dos and self.type == "out_invoice":
            self._get_warehouse()
