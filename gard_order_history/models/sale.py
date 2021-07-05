# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api, exceptions, _

from lxml import etree
import json

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_ids = fields.Many2many('account.invoice', string='Invoices', compute='_get_invoiced',
        copy=False, readonly=True, track_visibility='onchange')
    invoice_payment_ids = fields.Many2many('account.payment', string='Invoice Payments', compute='_get_invoice_payments',
        copy=False, readonly=True, track_visibility='onchange')

    @api.multi
    @api.depends('invoice_ids')
    def _get_invoice_payments(self):
        for order in self:
            if order.invoice_ids:
                order.invoice_payment_ids = order.mapped('invoice_ids').mapped('payment_ids')
                # _logger.debug('>>>>: %s', (order.invoice_payment_ids))

    @api.multi
    def button_order_history(self):
        return {
            'name': _('Sale Order History'),
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('gard_order_history.view_order_history_form').id,
            'context': {'turn_view_readonly': True},
            'res_id': self.id,
            'target': 'new',
        }


    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                           submenu=submenu)

        if context.get('turn_view_readonly'):  # Check for context value
            doc = etree.XML(res['arch'])
            if view_type == 'form':            # Applies only for form view
                for node in doc.xpath("//field"):   # All the view fields to readonly
                    node.set('readonly', '1')
                    node.set('modifiers', json.dumps({"readonly": True}))

                res['arch'] = etree.tostring(doc)
        return res

