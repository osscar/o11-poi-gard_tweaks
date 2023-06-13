# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import fields, models, _

# _logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    code = fields.Char(
        string="Short Code",
        size=10,
        required=True,
        help="The journal entries of this journal will be named using this prefix.",
    )
<<<<<<< Updated upstream
    note = fields.Text("Description")


# class AccountMove(models.Model):
#     _inherit = "account.move"

#     @api.multi
#     def write(self, vals):
#         req_model = request.params.get("model")
#         req_method = request.params.get("method")
#         post = (
#             req_model == "account.move" and req_method == "post"
#         )
#         invoice_refund = (
#             req_model == "account.invoice.refund" and req_method == "invoice_refund"
#         )
#         action_invoice_open = (
#             req_model == "account.invoice" and req_method == "action_invoice_open"
#         )
#         assign_outstanding_credit = (
#             req_model == "account.invoice" and req_method == "assign_outstanding_credit"
#         )
#         action_validate_invoice_payment = (
#             req_model == "account.payment" and req_method == "action_validate_invoice_payment"
#         )
#         immediate_transfer_process = (
#             req_method == "immediate.transfer.process"
#             # req_model == "stock" and 
#         )
#         payment_post = (
#             req_model == "account.payment" and req_method == "post"
#         )
#         payment_cancel = (
#             req_model == "account.payment" and req_method == "cancel"
#         )
#         process_reconciliations = (
#             req_model == "account.move.line" and req_method == "process_reconciliations"
#         )
#         rend_action_approve = req_model == ("account.expenses.rendition") and req_method == (
#             "action_approve"
#         )
#         rend_action_cancel = req_model == ("account.expenses.rendition") and req_method == (
#             "action_cancel"
#         )
#         process = req_model == ("stock.immediate.transfer") and req_method == (
#             "process"
#         )
#         inventory_action_done = req_model == ("stock.inventory") and req_method == (
#             "action_done"
#         )
#         fixable_automatic_asset = self.fixable_automatic_asset
#         group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")

#         allow_methods = (
#             post
#             or invoice_refund
#             or action_invoice_open
#             or action_validate_invoice_payment
#             or assign_outstanding_credit
#             or immediate_transfer_process
#             or payment_post
#             or payment_cancel
#             or process_reconciliations
#             or fixable_automatic_asset
#             or rend_action_approve
#             or rend_action_cancel
#             or process
#             or inventory_action_done
#         )
#         allow_groups = (
#             group_account_edit
#         )
#         allow_write = allow_methods or (allow_methods and allow_groups)
#         if any(
#             state != "draft"
#             for state in set(self.mapped("state"))
#             if allow_write == False
#         ):
#             raise UserError(
#                 _(
#                     "(%s) Edit allowed only in draft state. [%s.%s]"
#                     % (self, request.params.get("model"), request.params.get("method"))
#                 )
#             )
#         else:
#             # _logger.info('Written vals: %s' % vals)
#             return super().write(vals)
=======
    note = fields.Text("Description")
>>>>>>> Stashed changes
