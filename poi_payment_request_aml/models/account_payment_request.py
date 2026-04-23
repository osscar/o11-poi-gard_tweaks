from odoo import models, fields, api, _

class AccountPaymentRequest(models.Model):
    _inherit = "account.payment.request"

    move_line_ids = fields.Many2many(
        "account.move.line",
        string="Related Move Lines",
        compute="_compute_move_line_ids",
        help="Aggregated accounting lines from all related payments, movements, and renditions."
    )
    aml_count = fields.Integer(compute="_compute_aml_count", string="Journal Items Count")

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

    @api.depends('move_line_ids')
    def _compute_aml_count(self):
        for request in self:
            request.aml_count = len(request.move_line_ids)

    @api.multi
    def action_view_ledger_lines(self):
        self.ensure_one()
        # We create a clean context to prevent 'user_id' or other 
        # request-specific defaults from leaking into the move line view.
        ctx = {
            'search_default_group_by_account': 1, # Optional: nice for accountants
            'create': False,
            'edit': False,
        }
        
        return {
            'name': _('Journal Items'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [('id', 'in', self.move_line_ids.ids)],
            'context': ctx,
        }

    # aml payment request backfill method
    # disable after use
    @api.multi
    def action_backfill_aml_links(self):
        """Link existing data. Works for all requests regardless of selection."""
        # We search for ALL requests to ensure a complete backfill
        all_requests = self.env['account.payment.request'].search([])
        for request in all_requests:
            # Link direct payments
            if request.payment_ids:
                request.payment_ids.mapped('move_line_ids').write({'payment_request_id': request.id})
            
            # Link rendition moves and invoices
            if request.rendition_ids:
                request.rendition_ids.mapped('move_id.line_ids').write({'payment_request_id': request.id})
                request.rendition_ids.mapped('invoice_ids.move_id.line_ids').write({'payment_request_id': request.id})
            
            # Link cash movement payments
            if request.movement_ids:
                request.movement_ids.mapped('payment_ids.move_line_ids').write({'payment_request_id': request.id})
        return True