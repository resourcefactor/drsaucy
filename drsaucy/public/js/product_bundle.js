frappe.ui.form.on("Product Bundle Item", {
	custom_is_bom_item: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.custom_is_bom_item) {
			frappe.call({
				method: "drsaucy.hook_events.product_bundle.get_default_bom",
				args: {
					item_code: d.item_code,
				},
				callback: function (r) {
					frappe.model.set_value(cdt, cdn, "custom_bom", r.message);
				},
			});
		}
		else {
			frappe.model.set_value(cdt, cdn, "custom_bom", "");
		}
	},
});
