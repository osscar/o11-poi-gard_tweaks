#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# import logging

from odoo import api, fields, models, _
from openerp.addons.poi_bol_base.models.amount_to_text_es import to_word, MONEDAS

# _logger = logging.getLogger(__name__)


class ReportAccountInvoice(models.AbstractModel):
    _name = 'report.gard_x_gard.report_account_move_multi_t'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name(
            'gard_x_gard.report_account_move_multi_t')
        docs = self.env[report.model].browse(docids)
        line_obj = self.env['account.move.line']

        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'to_word': to_word,
            'get_payment': self._get_payment,
            'line_obj': line_obj,

        }

    @api.multi
    def _get_payment(self, move_id):
        if move_id.src:
            model, id = move_id.src.split(",")
            if model == 'account.payment':
                payment_id = self.env[model].browse(int(id))
                return payment_id
