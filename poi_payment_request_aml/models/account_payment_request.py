from odoo import models, fields, api

class AccountPaymentRequest(models.Model):
    _inherit = "account.payment.request"

    move_line_ids = fields.Many2many(
        "account.move.line",
        string="Related Move Lines",
        compute="_compute_move_line_ids",
        help="Aggregated accounting lines from all related payments, movements, and renditions."
    )

    @api.depends(
        'payment_ids.move_line_ids', 
        'rendition_ids.move_id.line_ids',
        'movement_ids.payment_ids.move_line_ids',
        'rendition_ids.invoice_ids.move_id.line_ids'
    )
    def _compute_move_line_ids(self):
        for request in self:
            # Gather lines from direct payments
            aml_ids = request.payment_ids.mapped('move_line_ids')
            
            # Gather lines from rendition moves
            aml_ids |= request.rendition_ids.mapped('move_id.line_ids')
            
            # Gather lines from cash movements
            aml_ids |= request.movement_ids.mapped('payment_ids.move_line_ids')
            
            # Gather lines from invoices linked to renditions
            aml_ids |= request.rendition_ids.mapped('invoice_ids.move_id.line_ids')

            request.move_line_ids = aml_ids