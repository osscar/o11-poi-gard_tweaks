# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _exception_check(self, vals):
        model, exc_field, exc_field_vals, msg = self._name, False, [], vals["exc_msg"]

        # check type
        check_type = vals["check_type"]
        if check_type == "state":
            exc_field = check_type
            exc_field_vals = ["draft"]

        # exception check values
        vals["exc_vals"] = {
            "model": model,
            "field": exc_field,
            "field_rec_vals": [getattr(self, exc_field)],
            "field_vals": exc_field_vals,
            "msg": msg,
        }

        result = self.env["propagate.exception"]._exception_check(vals)

        return result

    @api.one
    def button_create_cost_line(self):
        # check exceptions: state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only create cost lines if order is in the following states: ",
        }
        self._exception_check(vals)

        anl_lines = self.account_analytic_id.line_ids
        if not anl_lines:
            raise ValidationError(
                ("The analytic account has no analytic lines to propagate.")
            )

        for line in anl_lines:
            # set default product if no product
            # is set on landed cost line
            product_id = (
                line.product_id
                if line.product_id
                else self.env.ref("gard_x_propagate.product_slc_default")
            )

            # price_unit value needs to be inverted
            # to match landed cost value logic
            vals = {
                "cost_id": self.id,
                "account_analytic_line_id": line.id,
                "product_id": getattr(product_id, "id"),
                "split_method": getattr(product_id, "split_method"),
                "price_unit": line.amount * -1,
            }
            # _logger.debug('bclc vals >>>: %s', vals)

            new_lines = self.cost_lines.create(vals)
            new_lines.onchange_account_analytic_line_id()

        return True

    def button_unlink_cost_line(self):
        # check exceptions: state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only delete cost lines if order is in the following states: ",
        }
        self._exception_check(vals)

        # delete cost lines
        for line in self.cost_lines:
            line.unlink()

        return True


class LandedCostLine(models.Model):
    _inherit = "stock.landed.cost.lines"

    def _get_price_unit(self):
        price_unit = self.account_analytic_line_id.amount

        # convert currency if needed
        if (
            self.cost_id.account_journal_id.currency_id
            != self.account_analytic_line_id.currency_id
        ):
            price_unit = self.account_analytic_line_id.currency_id.compute(
                self.account_analytic_line_id.amount,
                self.cost_id.account_journal_id.currency_id,
            )

        # invert value to adapt to cost line logic
        price_unit = -price_unit

        return price_unit

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()

        # write onchange values
        if self.product_id:
            # get split_method
            self.split_method = self.product_id.split_method
        if self.account_analytic_line_id:
            # get unit price
            self.price_unit = self._get_price_unit()

        return res

    @api.onchange("account_analytic_line_id")
    def onchange_account_analytic_line_id(self):
        product_id = self.env.ref("gard_x_propagate.product_slc_default")
        if self.product_id:
            product_id = self.product_id

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
        self.price_unit = self._get_price_unit()
