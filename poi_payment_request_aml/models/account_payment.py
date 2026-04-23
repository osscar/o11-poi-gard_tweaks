from odoo import models, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        # 1. Run standard Odoo posting to create AMLs
        res = super(AccountPayment, self).post()

        for payment in self:
            # Resolve the Request ID through the hierarchy
            req_id = False
            
            if payment.payment_request_id:
                req_id = payment.payment_request_id.id
            elif payment.rendition_id and payment.rendition_id.request_id:
                req_id = payment.rendition_id.request_id.id
            elif payment.cash_movement_id and payment.cash_movement_id.payment_request_id:
                req_id = payment.cash_movement_id.payment_request_id.id
            
            # Stamp only the payment lines
            if req_id and payment.move_line_ids:
                payment.move_line_ids.write({'payment_request_id': req_id})
        return res