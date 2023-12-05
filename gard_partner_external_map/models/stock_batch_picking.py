# -*- encoding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    @api.multi
    def _open_route_map(self):
        for batch in self:
            return batch.picking_ids._open_route_map()