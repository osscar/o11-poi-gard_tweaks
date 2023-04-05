# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#import logging

from odoo import api, fields, models, _

#_logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    account_analytic_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account"
    )


class LandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"

    account_analytic_line_id = fields.Many2one(
        "account.analytic.line", string="Analytic Line"
    )
