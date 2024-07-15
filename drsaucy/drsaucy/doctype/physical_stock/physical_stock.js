// Copyright (c) 2021, Resource Factors DMCC and contributors
// For license information, please see license.txt

frappe.provide("erpnext.stock");

frappe.ui.form.on('Physical Stock', {
	refresh: function(frm) {
		if(frm.doc.docstatus < 1) {
			if (!frm.doc.posting_date) {
				const now = new Date();
				now.setDate(1);
				now.setDate(now.getDate() - 1);
				frm.set_value('posting_date', now);
			}

			frm.add_custom_button(__('Fetch Items from Warehouse'), function () {
				return frappe.call({
					method:"drsaucy.drsaucy.doctype.physical_stock.physical_stock.get_items",
					args: {
						warehouse: frm.doc.warehouse,
						company: frm.doc.company,
						item_group: frm.doc.item_group
					},
					callback: function(r) {
						var items = [];
						frm.clear_table("items");
						for(var i=0; i< r.message.length; i++) {
							var d = frm.add_child("items");
							$.extend(d, r.message[i]);
							if(!d.qty) d.qty = null;
							if(!d.valuation_rate) d.valuation_rate = null;
						}
						frm.refresh_field("items");
					}
				});
			});

			frm.add_custom_button(__('Record Full Consumption'), function () {
				$.each(frm.doc.items,  function(i,  d) {
					d.physical_stock = 0;
					d.stock_difference = d.available_stock;
					frm.refresh_fields();
				});
			});

			frm.set_query('warehouse', function(doc) {
				return {
					filters: {
						"company": doc.company
					}
				}
			});
		}
	},
	validate: function(frm) {
		$.each(frm.doc.items,  function(i,  d) {
			d.cost_center = frm.doc.cost_center;
			d.warehouse = frm.doc.warehouse;
			if(d.stock_difference < 0) {
				frappe.throw(__("Stock Difference Should be Greater than or Equal to 0"));
			} else if (d.physical_stock < 0) {
				frappe.throw(__("Physical Stock Should be Greater than or Equal to 0"));
			}
			d.consumption_amount = d.stock_difference * d.valuation_rate;
		});
	}
});

frappe.ui.form.on('Physical Stock Items', {
	// Calculate Stock Difference & Consumption Amount
	physical_stock: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.available_stock) {
			d.stock_difference = d.available_stock - d.physical_stock;
		}
		if (d.stock_difference && d.valuation_rate) {
			d.consumption_amount = d.stock_difference * d.valuation_rate;
		}
		else if (d.stock_difference == 0 && d.valuation_rate) {
			d.consumption_amount = d.stock_difference * d.valuation_rate;
		}
		frm.refresh_field("items");
	},
	stock_difference: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.stock_difference) {
			d.physical_stock = d.available_stock - d.stock_difference;
		}
		if (d.stock_difference && d.valuation_rate) {
			d.consumption_amount = d.stock_difference * d.valuation_rate;
		}
		frm.refresh_field("items");
	}
});
