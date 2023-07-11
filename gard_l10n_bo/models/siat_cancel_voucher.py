# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields

# _logger = logging.getLogger(__name__)


class SiatCancelVoucher(models.Model):
    _name = "siat.cancel.voucher"

    siat_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('cancelled', 'Cancelled'),
        ],
        string="Siat State",
        readonly=True,
        default='draft',
    )
    nit = fields.Char(string="NIT", required=True, help=".")
    base_dosif = fields.Char(string="Dosification", required=True, help=".")
    cc_nro = fields.Char(string="Invoice #", required=True, help=".")
    date_invoice = fields.Char(string="Invoice Date", required=True, help=".")
    cufd = fields.Char(string="CUFD", required=True, help=".")

    journal_id = fields.Many2one(
        "account.journal",
        related="warehouse_id.journal_id",
        string="Sale Journal",
        readonly=True,
    )
