from odoo import models, fields, api

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
        # Return an action to open the move line tree view filtered by this request
        return {
            'name': 'Journal Items',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [('id', 'in', self.move_line_ids.ids)],
            'context': dict(self._context, create=False),
        }

    # aml payment request backfill method
    # disable after use
    def action_backfill_aml_links(self):
        """One-time script to link existing AMLs to their Requests."""
        for request in self.search([]):
            # 1. Links from Direct Payments
            if request.payment_ids:
                request.payment_ids.mapped('move_line_ids').write({
                    'payment_request_id': request.id
                })
            
            # 2. Links from Renditions
            if request.rendition_ids:
                # Direct Rendition Moves
                request.rendition_ids.mapped('move_id.line_ids').write({
                    'payment_request_id': request.id
                })
                # Moves from Invoices linked to Renditions
                request.rendition_ids.mapped('invoice_ids.move_id.line_ids').write({
                    'payment_request_id': request.id
                })

            # 3. Links from Cash Movements
            if request.movement_ids:
                m_payments = request.movement_ids.mapped('payment_ids')
                m_payments.mapped('move_line_ids').write({
                    'payment_request_id': request.id
                })