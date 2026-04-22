from odoo import models, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        """Propagate Request ID to Move Lines upon posting."""
        res = super(AccountPayment, self).post()
        for payment in self:
            if payment.payment_request_id:
                # Odoo 11: move_line_ids contains all AMLs for the payment move
                payment.move_line_ids.write({
                    'payment_request_id': payment.payment_request_id.id
                })
        return res