# -*- coding: utf-8 -*-
import logging
import datetime
from odoo import models, fields, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_ids = fields.Many2many(
        "account.invoice",
        string='Invoices',
        compute="_get_invoiced",
        readonly=True,
        copy=False,
        track_visibility='onchange')
