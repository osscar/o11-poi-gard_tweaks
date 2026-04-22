class AccountExpensesRendition(models.Model):
    _inherit = "account.expenses.rendition"

    def action_done(self):
        """Stamp rendition move lines with the Request ID."""
        res = super(AccountExpensesRendition, self).action_done()
        for rendition in self:
            if rendition.request_id and rendition.move_id:
                rendition.move_id.line_ids.write({
                    'payment_request_id': rendition.request_id.id
                })
        return res