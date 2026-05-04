from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_request_id = fields.Many2one(
        "account.payment.request", 
        string="Payment Request",
        index=True,
        help="The payment request that generated or is linked to this journal entry line."
    )