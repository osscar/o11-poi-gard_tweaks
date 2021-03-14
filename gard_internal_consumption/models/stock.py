# -*- coding: utf-8 -*-
# import logging
from odoo import models, fields, api, exceptions, _

# _logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_internal_consumption = fields.Boolean(string='Internal Consumption', readonly=True, store=True, help="Selected if this is an internal consumption picking.")


class StockMove(models.Model):
    _inherit = "stock.move"

    is_internal_consumption = fields.Boolean(string='Internal Consumption', readonly=True, store=True, help="Selected if this is an internal consumption move.")

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new and self.sale_line_id and self.sale_line_id.order_id and self.sale_line_id.order_id.is_internal_consumption == True:
            self.picking_id.message_post_with_view(
                'gard_internal_consumption.track_internal_consumption_move',
                values={'self': self.picking_id, 'origin': self.sale_line_id.order_id},
                subtype_id=self.env.ref('mail.mt_note').id)

    def _get_new_picking_values(self):
        res = super(StockMove,self)._get_new_picking_values()
        res.update({'is_internal_consumption': self.sale_line_id and self.sale_line_id.order_id and self.sale_line_id.order_id.is_internal_consumption})
        return res
