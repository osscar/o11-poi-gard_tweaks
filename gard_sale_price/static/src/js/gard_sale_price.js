openerp.gard_sale_price = function(instance) {
var QWeb = openerp.web.qweb;
    _t = instance.web._t;

instance.web.View.include({
    load_view: function(context) {
        var self = this;
        var view_loaded_def;
        $('#sale_pricelist_items').click(this.button_product_pricelist_items);

//this is button class which call method for open your form.

    return self._super(context);
    },

    button_product_pricelist_items: function(sale_price){
        sale_price.preventDefault();
        var self = this;
        var product_id = self.product_id.id
            this.do_action({
        // product_id = self.product_id.id
                'type': 'ir.actions.act_window',
                'name': 'Pricelist Items',
                'res_model': 'product.pricelist.item',
                'domain': [('product_id', '=', product_id)],
                'view_id': False,
                'view_mode': 'tree',
                'context': {},
                'target': 'new',
            });
        },
});
};

                // name: _t("View name"),
                // type: "ir.actions.act_window",
                // res_model: "object",
                // domain : [],
                // views: [[false, "list"],[false, "tree"]],
                // target: 'new',
                // context: {},
                // view_type : 'list',
                // view_mode : 'list'


