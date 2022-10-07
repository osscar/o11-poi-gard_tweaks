# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # @api.one
    @api.depends("state")
    def _get_warehouse(self):
        res = super(AccountInvoice, self)._get_warehouse()
        if self.cc_dos and self.type == "out_invoice":
            if self.cc_dos and not self.cc_dos.warehouse_id.journal_id:
                raise ValidationError(
                    _("A journal must be set for the dosification branch.")
                )
            else:
                # set appropriate sale journal based on cc_dos.warehouse_id.journal_id
                self.journal_id = self.cc_dos.journal_id
                # self.write({"journal_id": self.cc_dos.journal_id.id})
        return res

    @api.onchange("cc_dos")
    # @api.one
    def _onchange_cc_dos(self):
        # self.ensure_one()
        if self.cc_dos and self.type == "out_invoice":
            # onchange cc_dos set cc_dos sale journal
            # self.env["account.journal"].search(
            #     [("id", "=", self.cc_dos.journal_id.id)]
            # )  
            self._get_warehouse()
            # self.journal_id = self.cc_dos.journal_id
