# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import models, _

# _logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"
    _order = "date desc"


class LandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"
    _order = "product_id asc"
