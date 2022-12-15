# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    @api.one
    def button_cost_line_create(self):
        anl_lines = self.account_analytic_id.line_ids
        for line in anl_lines:
            # _logger.debug('bclc vals >>>: %s', line)
            if line.product_id:
                # _logger.debug('bclc if product_id vals >>>: %s', line.product_id)
                product_id = line.product_id
            else:
                # _logger.debug('bclc else product_id vals >>>: %s', line.product_id)
                product_id = self.env.ref('gard_x_stock_landed_costs.product_slc_default')
            vals = {
                'cost_id': self.id,
                'account_analytic_line_id': line.id,
                'product_id': product_id.id,
                'split_method': product_id.split_method,
                'price_unit': line.amount * -1,
            }
            # _logger.debug('bclc vals >>>: %s', vals)

            new_lines = self.cost_lines.create(vals)
            new_lines.onchange_account_analytic_line_id()
        return True

    def button_cost_line_unlink(self):
        for line in self.cost_lines:
            line.unlink()
        return True


class LandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super(LandedCostLine, self).onchange_product_id()
        if self.account_analytic_line_id:
            # convert currency if needed
            if (
                self.cost_id.account_journal_id.currency_id
                != self.account_analytic_line_id.currency_id
            ):
                price_unit = self.account_analytic_line_id.currency_id.compute(
                    self.account_analytic_line_id.amount,
                    self.cost_id.account_journal_id.currency_id,
                )
            else:
                price_unit = self.account_analytic_line_id.amount
            self.price_unit = -1 * price_unit
        return res

    @api.onchange("account_analytic_line_id")
    def onchange_account_analytic_line_id(self):
        if self.product_id:
            # _logger.debug('bclc if product_id vals >>>: %s', self.product_id)
            product_id = self.product_id
        # use default product if analytic line doe not have aproduct_id assigned
        else:
            # _logger.debug('bclc else product_id vals >>>: %s', self.product_id)
            product_id = self.env.ref('gard_x_stock_landed_costs.product_slc_default')
        # write values to cost line fields
        self.product_id = product_id
        self.name = (
            str(self.account_analytic_line_id.ref)
            + " "
            + str(self.account_analytic_line_id.name)
        )
        self.account_id = self.account_analytic_line_id.general_account_id
        self.analytic_account_id = self.account_analytic_line_id.account_id
        self.analytic_tag_ids = self.account_analytic_line_id.tag_ids
        # convert currency if needed
        if (
            self.cost_id.account_journal_id.currency_id
            != self.account_analytic_line_id.currency_id
        ):
            price_unit = self.account_analytic_line_id.currency_id.compute(
                self.account_analytic_line_id.amount,
                self.cost_id.account_journal_id.currency_id,
            )
        else:
            price_unit = self.account_analytic_line_id.amount
        self.price_unit = price_unit * -1
