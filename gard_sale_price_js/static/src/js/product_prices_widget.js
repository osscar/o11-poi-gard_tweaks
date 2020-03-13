odoo.define('product_prices.widget', function (require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var form_common = require('web.form_common');
var ListView = require('web.ListView');
// var form_common = require('web.form_common');
// var formats = require('web.formats');
// var Model = require('web.Model');
// var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var ShowProductPricesWidget = ListView.extend({

    init: function(parent, context) {
        // this._super(parent);
        this.lines = []; // list of reconciliations identifiers to instantiate children widgets         this.model_pli = new Model("product.pricelist.item");
        this.context = context;
        this.data = context.data;
        this.set("mv_lines_selected", []);
    },

    loadData: function() {
        var self = this;
    },

    render_product_prices: function() {
        var self = this;
        return this
            .call("_get_product_prices_info_JSON")
            .then(function (lines)) {
                _.each(lines, function(line), self);
                callback.call(self, lines);
            }




    // updateAccountingViewMatchedLines: function() {
        // var self = this;
        // $.each(self.$(".tbody_matched_lines .bootstrap_popover"), function(){ $(this).popover('destroy') });
        // self.$(".tbody_matched_lines").empty();

        // var template_name = (QWeb.has_template(this.template_prefix+"reconciliation_move_line") ? this.template_prefix : "") + "reconciliation_move_line";
        _(self.get("mv_lines_selected")).each(function(line){
            // line.amount_str = self.formatCurrencies(Math.abs(line.debit + line.credit), self.get("currency_id"));
            var $line = $(QWeb.render('ShowProductPricesInfo', {line: line}));
            self.bindPopoverTo($line.find(".line_info_button"));
            if (line.propose_partial_reconcile) self.bindPopoverTo($line.find(".do_partial_reconcile_button"));
            if (line.partial_reconcile) self.bindPopoverTo($line.find(".undo_partial_reconcile_button"));
            self.$(".tbody_matched_lines").append($line);
        });
    },

    updateMatchesGetMvLines: function(excluded_ids, offset, limit, callback) {
        var self = this;
        return self.model_aml
            .call("get_move_lines_for_manual_reconciliation", [
                self.data.account_id,
                self.data.partner_id || undefined,
                excluded_ids,
                self.filter,
                offset,
                limit,
                self.get("currency_id") ])
            .then(function (lines) {
                _.each(lines, function(line) { self.decorateMoveLine(line) }, self);
                callback.call(self, lines);
            });
    },




        return self.model_aml
            .call("_get_pricelist_items", [


        self.$el.prepend(QWeb.render("ShowProductPricesInfo", {
            data: self.data,

            this.$el.html(QWeb.render('ShowProductPricesInfo', {
                'lines': info.content,
                // 'outstanding': info.outstanding,
                'title': info.title
            }));
            // _.each(this.$('.js_product_prices_info'), function(){
            _(self.get("product_prices")).each(function(){
                self.$(".js_product_prices_info").empty().append($line);

                // var template_name = QWeb.render('PricesPopOver', {
                var options = {
                    'content': QWeb.render('PricesPopOver', {
                            'name': info.content.name,
                            'min_quantity': info.content.min_quantity,
                            'sale_price': info.content.sale_price,
                            'unit_price': info.content.unit_price,
                            'pricelist_id': info.content.pricelist_id,
                            'partner_ids': info.content.partner_ids,
                            }),
                    'html': true,
                    'placement': 'left',
                    'title': _t('Pricelist Items'),
                    'trigger': 'focus',
                    'delay': { "show": 0, "hide": 100 },
                };
            });
        }
        else {
            this.$el.html('');
        }
    },
});

core.list_widget_registry.add('product_prices', ShowProductPricesWidget);

});
