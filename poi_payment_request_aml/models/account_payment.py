from odoo import models, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        # 1. Let the base module and Odoo standard logic run first.
        # This creates the journal entries and move lines.
        res = super(AccountPayment, self).post()

        # 2. Now that the lines exist, stamp them with the Request ID
        for payment in self:
            if payment.payment_request_id and payment.move_line_ids:
                payment.move_line_ids.write({
                    'payment_request_id': payment.payment_request_id.id
                })
        return res