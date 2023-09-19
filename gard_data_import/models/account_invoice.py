# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _rec_name = "record_name"
    
    record_name = fields.Char('Complete Name', compute='_compute_record_name', store=True)
    refund_request_ids = fields.One2many(
        comodel_name="account.invoice.refund.request",
        inverse_name="invoice_id",
        readonly=True,
    )
    # state_refund_request = fields.Selection(
    #     related="refund_request_ids.state",
    #     readonly=True,
    #     track_visibility="onchange",
    # )
    
    @api.depends('number', 'origin', "cc_nro")
    def _compute_record_name(self):
        for invoice in self:
            _logger.debug("_crn self >>>: %s", invoice)
            ref = invoice.cc_nro or invoice.supplier_invoice_number or invoice.reference
            origin = invoice.origin
            
            record_name = invoice.number
            _logger.debug("_crn ref >>>: %s", ref)
            _logger.debug("_crn origin >>>: %s", origin)
            _logger.debug("_crn rn >>>: %s", record_name)
            if ref:
                record_name = '%s: F%s' % (record_name, ref)
                _logger.debug("_crn if ref rn >>>: %s", record_name)
            if origin:
                record_name = '%s / %s' % (record_name, origin)
                _logger.debug("_crn if origin rn >>>: %s", record_name)
                
            invoice.record_name = record_name
            _logger.debug("_crn if ref rn >>>: %s", record_name)
