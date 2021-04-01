# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    force_date = fields.Datetime('Force Date')

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()

        # write transfer date with forced date if forced
        for pick in self:
            if pick.force_date:
                pick.write({'date_done': pick.force_date})

        return res

    # TO DO created picks to force date should be name sequenced with forced date for sequences with date variables
    # @api.model
    # def create(self, vals):
    #     if self.force_date != False:
    #         defaults = self.default_get(['name', 'picking_type_id'])
    #         if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
    #             vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id(ir_sequence_date=self.force_date)

    #         if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
    #             for move in vals['move_lines']:
    #                 if len(move) == 3 and move[0] == 0:
    #                     move[2]['location_id'] = vals['location_id']
    #                     move[2]['location_dest_id'] = vals['location_dest_id']
    #         res = super(Picking, self).create(vals)
    #         res._autoconfirm_picking()
    #         return res
    #     else:
    #         return super(StockPicking, self).create(vals)
