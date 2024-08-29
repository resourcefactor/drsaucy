// Copyright (c) 2024, RF and contributors
// For license information, please see license.txt

frappe.ui.form.on("BlinkCo Orders", {
	refresh: function (frm) {
		frm.page.btn_secondary.hide();
		frm.disable_save();
	},
});
