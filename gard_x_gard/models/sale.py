# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    team_id = fields.Many2one(
        "crm.team",
        "Sales Channel",
        change_default=False,
        default=False,
        track_visibility="onchange",
    )

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        inv_ids = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, final=final
        )
        invoice_obj = self.env["account.invoice"]
        invoices = invoice_obj.browse(inv_ids)

        for inv in invoices:
            inv.write(
                {
                    "nit": self.partner_invoice_id.nit or self.partner_invoice_id.ci,
                    "razon": self.partner_invoice_id.razon,
                    "contract_nr": self.contract_nr,
                }
            )

        return inv_ids


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    date_order_id = fields.Datetime(
        "Order Date",
        related="order_id.date_order",
        readonly=True,
        index=True,
    )