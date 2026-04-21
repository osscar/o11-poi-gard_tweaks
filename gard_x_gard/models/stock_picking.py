# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "date_done desc, create_date desc"

    requested_by = fields.Many2one(
        "res.users",
        "Requested By",
        readonly=True,
        help="User that requested this transfer.",
    )
    # Category based on location/destination usage
    category = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('customer_delivery', 'Customer Delivery'),
        ('supplier_return', 'Supplier Return'),
        ('supplier_shipment', 'Supplier Shipment'),
        ('customer_return', 'Customer Return'),
        ('other', 'Other')
    ], "Category", compute="_compute_category", store=True)

    @api.depends('picking_type_id', 'location_id.usage', 'location_dest_id.usage')
    def _compute_category(self):
        for picking in self:
            # Cache variables to avoid repeated dot-notation lookups
            pt_code = picking.picking_type_code
            src_usage = picking.location_id.usage
            dest_usage = picking.location_dest_id.usage
            
            # Default value
            category = 'other'

            if pt_code == 'internal' or src_usage in ['internal', 'transit'] and dest_usage in ['internal', 'transit']:
                category = 'internal'
            
            elif pt_code == 'incoming':
                if src_usage == 'supplier':
                    category = 'supplier_shipment'
                elif dest_usage == 'supplier':
                    category = 'supplier_return'
                elif src_usage == 'customer':
                    category = 'customer_return'
                elif dest_usage in ['internal', 'transit']:
                    category = 'internal'
                    
            elif pt_code == 'outgoing':
                if dest_usage == 'customer':
                    category = 'customer_delivery'
                elif src_usage == 'customer':
                    category = 'customer_return'
                elif dest_usage == 'supplier':
                    category = 'supplier_return'
                elif src_usage in ['internal', 'transit']:
                    category = 'internal'

            picking.category = category
    
